import { useState, useEffect, useRef } from "react";
import useAnnotationsStore from "./stores/annotations";

const { importWhiteboxComponent, importWhiteboxStateStore, withStateStore } =
  Whitebox;

const Button = importWhiteboxComponent("ui.button");
const ChatIcon = importWhiteboxComponent("icons.chat");
const ArrowCircleUpIcon = importWhiteboxComponent("icons.arrow-circle-up");
const ScrollableOverlay = importWhiteboxComponent("ui.scrollable-overlay");

const Avatar = ({ initial, bordered = false }) => {
  return (
    <div
      className={`w-10 h-10 bg-gray-5 rounded-full flex items-center justify-center text-gray-1 font-medium ${
        bordered ? "border-2 border-gray-4" : ""
      }`}
    >
      {initial}
    </div>
  );
};

const formatTime = (timestamp) => {
  const date = new Date(timestamp);
  return date.toLocaleTimeString("en-US", {
    hour12: false,
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
};

const AnnotationCard = ({ annotation }) => {
  return (
    <div className="flex flex-row gap-2 border border-gray-4 p-4 rounded-3xl">
      <div>
        <Avatar initial={annotation.avatar_initial} bordered />
      </div>
      <div className="flex flex-col">
        <div className="flex items-center justify-between gap-2 mb-1">
          <h1 className="text-gray-1 font-bold">{annotation.author_name}</h1>
          <p className="text-sm text-gray-2">
            {formatTime(annotation.timestamp)}
          </p>
        </div>
        <p className="text-gray-1 text-md">{annotation.message}</p>
      </div>
    </div>
  );
};

const AnnotationsToWrap = () => {
  const annotations = useAnnotationsStore((state) => state.annotations);
  const sendAnnotation = useAnnotationsStore((state) => state.sendAnnotation);
  const initializeWebSocket = useAnnotationsStore(
    (state) => state.initializeWebSocket
  );

  // Check if flight is active
  const useMissionControlStore = importWhiteboxStateStore(
    "flight.mission-control"
  );

  const missionControlMode = useMissionControlStore((state) => state.mode);
  const activeFlightSession = useMissionControlStore(
    (state) => state.activeFlightSession
  );

  const isPlayback = missionControlMode === "playback";
  const isFlightActive =
    missionControlMode === "flight" && activeFlightSession?.ended_at === null;

  const [inputMessage, setInputMessage] = useState("");
  const [authorName, setAuthorName] = useState("Unknown");
  const scrollableRef = useRef(null);

  // Initialize WebSocket on mount
  useEffect(() => {
    const cleanup = initializeWebSocket();
    return cleanup;
  }, [initializeWebSocket]);

  // Auto-scroll to bottom when annotations change
  useEffect(() => {
    if (scrollableRef.current) {
      scrollableRef.current.scrollTop = scrollableRef.current.scrollHeight;
    }
  }, [annotations]);

  const handleSendAnnotation = () => {
    if (!inputMessage.trim() || !isFlightActive) {
      return;
    }

    sendAnnotation(inputMessage, authorName);
    setInputMessage("");
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      handleSendAnnotation();
    }
  };

  return (
    <ScrollableOverlay
      openOverlayIcon={<ChatIcon />}
      overlayTitle="Annotations"
      overlaySubtitle={`(${annotations.length})`}
    >
      {/* Annotations - Scrollable */}
      <div
        ref={scrollableRef}
        className="overflow-y-auto p-4 space-y-4 flex-1 max-h-64"
      >
        {annotations.length === 0 ? (
          <div className="text-center text-gray-4 py-8">
            {isFlightActive || isPlayback
              ? "No annotations yet"
              : "No flight session active"}
          </div>
        ) : (
          annotations.map((annotation) => (
            <AnnotationCard key={annotation.id} annotation={annotation} />
          ))
        )}
      </div>

      {/* Annotation input */}
      <div className="p-4 border-t border-gray-5 flex-shrink-0">
        <div className="flex items-center gap-3">
          <Avatar initial={authorName[0]?.toUpperCase() || "P"} />
          <div className="flex-1 relative">
            <input
              type="text"
              placeholder={
                isFlightActive
                  ? "Add an annotation..."
                  : "Start a flight to add annotations"
              }
              className="w-full px-4 py-3 bg-gray-50 rounded-full text-sm text-gray-1 placeholder-gray-4 border border-gray-4 focus:outline-none focus:ring-2 focus:ring-gray-3 focus:border-transparent"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={!isFlightActive}
            />
            <div className="absolute right-1 top-1/2 transform -translate-y-1/2">
              <Button
                leftIcon={<ArrowCircleUpIcon />}
                onClick={handleSendAnnotation}
                disabled={!inputMessage.trim() || !isFlightActive}
              />
            </div>
          </div>
        </div>
      </div>
    </ScrollableOverlay>
  );
};

const Annotations = withStateStore(AnnotationsToWrap, [
  "flight.mission-control",
]);

export default Annotations;
export { Annotations };
