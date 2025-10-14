import Annotations from "./Annotations";

const {
  importWhiteboxStateStore,
  withStateStore,
} = Whitebox;

const AnnotationsOverlayToWrap = (props) => {
  const useMissionControlStore = importWhiteboxStateStore("flight.mission-control");
  const mode = useMissionControlStore((state) => state.mode);
  const isFlightActive = useMissionControlStore(
    (state) => state.isFlightSessionActive()
  );

  const shouldShowOverlay = mode === "playback" || isFlightActive;
  if (!shouldShowOverlay)
    return null;

  return (
      <Annotations {...props} />
  );
}

const AnnotationsOverlay = withStateStore(
  AnnotationsOverlayToWrap,
  ["flight.mission-control"],
)

export { AnnotationsOverlay };
export default AnnotationsOverlay;
