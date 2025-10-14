import { useState } from "react";
import useAnnotationsStore from "./stores/annotations";
import Avatar from "./Avatar";

const { importWhiteboxComponent } = Whitebox;

const Button = importWhiteboxComponent("ui.button");
const ArrowCircleUpIcon = importWhiteboxComponent("icons.arrow-circle-up");

const AnnotationInput = () => {
  const sendAnnotation = useAnnotationsStore((state) => state.sendAnnotation);

  const [inputMessage, setInputMessage] = useState("");
  const [authorName, setAuthorName] = useState("Unknown");

  const handleSendAnnotation = () => {
    if (!inputMessage.trim()) {
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
      <div className="p-4 border-t border-gray-5 flex-shrink-0">
        <div className="flex items-center gap-3">
          <Avatar initial={authorName[0]?.toUpperCase() || "P"} />
          <div className="flex-1 relative">
            <input
              type="text"
              placeholder="Add an annotation..."
              className={"w-full px-4 py-3 bg-gray-50 rounded-full text-sm "
                         + "text-gray-1 placeholder-gray-4 border border-gray-4 "
                         + "focus:outline-none focus:ring-2 focus:ring-gray-3 "
                         + "focus:border-transparent"}
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyDown={handleKeyDown}
            />
            <div className="absolute right-1 top-1/2 transform -translate-y-1/2">
              <Button
                leftIcon={<ArrowCircleUpIcon />}
                onClick={handleSendAnnotation}
                disabled={!inputMessage.trim()}
              />
            </div>
          </div>
        </div>
      </div>
  )
}

export default AnnotationInput;
