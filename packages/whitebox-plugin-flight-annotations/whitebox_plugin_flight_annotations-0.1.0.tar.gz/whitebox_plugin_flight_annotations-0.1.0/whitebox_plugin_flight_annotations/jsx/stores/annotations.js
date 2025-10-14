import { create } from "zustand";

const annotationsStore = (set, get) => ({
  annotations: [],
  isLoading: false,

  sendAnnotation: (message, authorName = "Unknown") => {
    if (!message.trim()) return;

    Whitebox.sockets.send("flight", {
      type: "flight.annotation.send",
      message: message.trim(),
      author_name: authorName.trim(),
    });
  },

  loadAnnotations: () => {
    set({ isLoading: true });
    Whitebox.sockets.send("flight", {
      type: "flight.annotations.load",
    });
  },

  // Initialize WebSocket listeners
  initializeWebSocket: () => {
    const cleanup = Whitebox.sockets.addEventListener(
      "flight",
      "message",
      (event) => {
        const data = JSON.parse(event.data);

        if (data.type === "flight.annotations.list") {
          set({
            annotations: data.annotations || [],
            isLoading: false,
          });
        }
      }
    );

    if (get().annotations.length === 0) {
      get().loadAnnotations();
    }

    return cleanup;
  },
});

const useAnnotationsStore = create(annotationsStore);

export default useAnnotationsStore;
