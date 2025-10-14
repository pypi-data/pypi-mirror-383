import { useEffect } from "react";
import useAnnotationsStore from "./stores/annotations";

const { importWhiteboxStateStore, withStateStore } = Whitebox;

const AnnotationsServiceComponentToWrap = () => {
  const useMissionControlStore = importWhiteboxStateStore("flight.mission-control");
  const onMissionControlEvent = useMissionControlStore((state) => state.on);

  const setAnnotations = useAnnotationsStore((state) => state.setAnnotations);

  const requestFlightAnnotations = (flightSession) => {
    Whitebox.sockets.send("flight", {
      type: "flight.annotation.load",
      flight_session_id: flightSession?.id,
    });
  }

  const requestFlightAnnotationsOnMount = () => {
    // In case that the flight is active, and the component is being mounted
    // after flight session has been set in the state store - the `mode` event
    // would've already been propagated, we won't fetch the initial state of
    // the flight's annotations. Detect that and load if needed

    // Get state without subscription
    const {
      mode,
      activeFlightSession,
    } = useMissionControlStore.getState();

    if (mode === "flight" && activeFlightSession)
      requestFlightAnnotations(activeFlightSession);
  }

  useEffect(() => {
    const unmountCallbacks = [];

    // Keep annotations store up to date with the incoming info
    unmountCallbacks.push(
        Whitebox.sockets.addEventListener("flight", "message", (event) => {
          const data = JSON.parse(event.data);

          if (data.type === "flight.annotation.list") {
            setAnnotations(data.annotations);
          }
        }),
    );

    // Request new data on mode change
    unmountCallbacks.push(
        onMissionControlEvent("mode", (type, flightSession) => {
          // In case we are in flight mode, but without an active flight session
          // don't do anything here
          if (!flightSession || flightSession.ended_at)
            return;

          requestFlightAnnotations(flightSession);
        }),
    );

    // By this time, event listener has been hooked up, so we can request them
    requestFlightAnnotationsOnMount();

    // Cleanup on unmount
    return () => unmountCallbacks.forEach((callback) => callback());
  }, []);

  return null;
}

const AnnotationsServiceComponent = withStateStore(
    AnnotationsServiceComponentToWrap,
    ["flight.mission-control", "flight.annotations"],
)

export { AnnotationsServiceComponent };
export default AnnotationsServiceComponent;
