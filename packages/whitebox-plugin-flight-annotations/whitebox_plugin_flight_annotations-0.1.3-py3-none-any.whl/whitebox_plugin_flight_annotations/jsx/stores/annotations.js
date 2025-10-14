import { create } from "zustand";

const annotationsStore = (set, get) => ({
  annotations: [],

  sendAnnotation: (message, authorName = "Unknown") => {
    if (!message.trim()) return;

    Whitebox.sockets.send("flight", {
      type: "flight.annotation.send",
      message: message.trim(),
      author_name: authorName.trim(),
    });
  },

  setAnnotations: (annotations) => set({ annotations }),
});

const useAnnotationsStore = create(annotationsStore);

export default useAnnotationsStore;
