import Avatar from "./Avatar";

const { importWhiteboxStateStore } = Whitebox;

const AnnotationCard = ({ annotation, flightSession, status }) => {
  const useMissionControlStore = importWhiteboxStateStore("flight.mission-control");
  const setPlaybackTime = useMissionControlStore((state) => state.setPlaybackTime);

  let styling;
  switch (status) {
    case "past":
      styling = "border-medium-emphasis";
      break;
    case "current":
      styling = "border-high-emphasis";
      break;
    case "upcoming":
      styling = "border-low-emphasis opacity-60";
      break;
  }

  const annotationTimestamp = Whitebox.utils.humanize.formatDuration(
      new Date(flightSession.started_at),
      new Date(annotation.timestamp),
  );

  const outerClassName = Whitebox.utils.getClasses(
      "flex flex-row gap-2 border p-4 rounded-3xl",
      styling,
  );

  const setPlaybackTimeToAnnotation = () => {
    // In active flight session's context, there is no playback time to set
    if (!flightSession.ended_at)
      return;

    const timestamp = new Date(annotation.timestamp);
    setPlaybackTime(timestamp, true);
  }

  return (
    <div className={outerClassName}>
      <div>
        <Avatar initial={annotation.avatar_initial} bordered />
      </div>
      <div className="flex flex-col">
        <div className="flex items-center justify-between gap-2 mb-1">
          <h1 className="text-gray-1 font-bold">{annotation.author_name}</h1>
          <p className="text-sm text-gray-2"
             onClick={setPlaybackTimeToAnnotation}>
            {annotationTimestamp}
          </p>
        </div>
        <p className="text-gray-1 text-md">{annotation.message}</p>
      </div>
    </div>
  );
};

export default AnnotationCard;
