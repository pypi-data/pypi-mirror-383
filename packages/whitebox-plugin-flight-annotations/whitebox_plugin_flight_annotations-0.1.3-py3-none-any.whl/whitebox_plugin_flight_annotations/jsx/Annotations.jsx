import { useState, useEffect, useRef } from "react";
import useAnnotationsStore from "./stores/annotations";
import AnnotationCard from "./AnnotationCard";
import AnnotationInput from "./AnnotationInput";

const {
  importWhiteboxComponent,
  importWhiteboxStateStore,
  withStateStore,
} = Whitebox;

const ChatIcon = importWhiteboxComponent("icons.chat");
const ScrollableOverlay = importWhiteboxComponent("ui.scrollable-overlay");

const AnnotationList = ({ annotations }) => {
  const useMissionControlStore = importWhiteboxStateStore("flight.mission-control");
  const onMissionControlEvent = useMissionControlStore((state) => state.on);
  const flightSession = useMissionControlStore((state) => state.getFlightSession());

  const [activeAnnotationIndex, setActiveAnnotationIndex] = useState(-1);
  const sortedAnnotations = annotations.sort((a, b) => {
    return a.timestamp - b.timestamp;
  });

  useEffect(() => {
    return onMissionControlEvent("playback.time", (time, unixTime) => {
      console.log('Time!', time, "unix", unixTime);
      // Every element in `sortedAnimations` has `playback` unix timestamp
      // Find the index of the element within it that is the last one before
      // the `unixTime` specified here
      let latest = -1
      for (let i = 0; i < sortedAnnotations.length; i++) {
        const timestamp = new Date(sortedAnnotations[i].timestamp);
        if (timestamp <= unixTime) {
          latest = i;
        }
      }

      setActiveAnnotationIndex(latest);
    });
  }, [sortedAnnotations, onMissionControlEvent]);

  const flightSessionActive = !flightSession.ended_at;

  return sortedAnnotations.map((annotation, index) => {
    let status;
    if (index < activeAnnotationIndex || flightSessionActive)
      status = "past";
    else if (index === activeAnnotationIndex)
      status = "current";
    else
      status = "upcoming";

    return <AnnotationCard key={annotation.id}
                           annotation={annotation}
                           flightSession={flightSession}
                           status={status} />
  })
}

const AnnotationListContainer = () => {
  const annotations = useAnnotationsStore((state) => state.annotations);
  const ref = useRef(null);

  // Auto-scroll to bottom when annotations change
  useEffect(() => {
    if (ref.current) {
      ref.current.scrollTop = ref.current.scrollHeight;
    }
  }, [annotations]);

  const content = (annotations.length > 0) ? (
      <AnnotationList annotations={annotations} />
  ) : (
      <div className="text-center text-gray-4 py-8">
        No annotations yet
      </div>
  );

  return (
      <div ref={ref}
           className="overflow-y-auto p-4 space-y-4 flex-1 max-h-64">
        {content}
      </div>
  )
}

const AnnotationsToWrap = () => {
  const useMissionControlStore = importWhiteboxStateStore("flight.mission-control");
  const isFlightActive = useMissionControlStore((state) => state.isFlightSessionActive());

  const annotations = useAnnotationsStore((state) => state.annotations);

  return (
    <ScrollableOverlay
      openOverlayIcon={<ChatIcon />}
      overlayTitle="Annotations"
      overlaySubtitle={`(${annotations.length})`}
    >
      <AnnotationListContainer />
      {isFlightActive && <AnnotationInput />}
    </ScrollableOverlay>
  );
};

const Annotations = withStateStore(
  AnnotationsToWrap,
  ["flight.mission-control"],
)

export default Annotations;
export { Annotations };
