import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import AnnotationInput from "./AnnotationInput";
import useAnnotationsStore from "./stores/annotations";

describe("AnnotationInput", () => {
  const setState = useAnnotationsStore.setState;

  it("renders input", async () => {
    render(<AnnotationInput />);

    expect(
      screen.getByPlaceholderText("Add an annotation...")
    ).toBeInTheDocument();
  });

  it("disables button for empty/whitespace and enables for text", async () => {
    const user = userEvent.setup();
    const { container } = render(<AnnotationInput />);

    const input = screen.getByPlaceholderText("Add an annotation...");
    const btn = container.querySelector('button');

    expect(btn).toBeDisabled();

    await user.type(input, "   ");
    expect(btn).toBeDisabled();

    await user.clear(input);
    await user.type(input, "Hello");
    expect(btn).not.toBeDisabled();

    await user.clear(input);
    expect(btn).toBeDisabled();
  });

  it("clicking send calls store.sendAnnotation(message, 'Unknown') and clears input", async () => {
    const mockSendAnnotation = vi.fn();
    setState({ sendAnnotation: mockSendAnnotation });

    const user = userEvent.setup();
    const { container } = render(<AnnotationInput />);

    const input = screen.getByPlaceholderText("Add an annotation...");
    const btn = container.querySelector('button');

    await user.type(input, "  Possible pilot deviation  ");
    await user.click(btn);

    expect(mockSendAnnotation).toHaveBeenCalledTimes(1);
    expect(mockSendAnnotation).toHaveBeenCalledWith(
      "  Possible pilot deviation  ",
      "Unknown"
    );
    expect(input).toHaveValue("");
  });

  it("pressing Enter sends (when non-empty) and clears input", async () => {
    const mockSendAnnotation = vi.fn();
    setState({ sendAnnotation: mockSendAnnotation });

    const user = userEvent.setup();
    render(<AnnotationInput />);

    const input = screen.getByPlaceholderText("Add an annotation...");
    await user.type(input, "Check this moment{enter}");

    expect(mockSendAnnotation).toHaveBeenCalledTimes(1);
    expect(mockSendAnnotation).toHaveBeenCalledWith("Check this moment", "Unknown");
    expect(input).toHaveValue("");
  });

  it("pressing Enter with only whitespace does not send", async () => {
    const mockSendAnnotation = vi.fn();
    setState({ sendAnnotation: mockSendAnnotation });

    const user = userEvent.setup();
    render(<AnnotationInput />);

    const input = screen.getByPlaceholderText("Add an annotation...");
    await user.type(input, "   {enter}");

    expect(mockSendAnnotation).not.toHaveBeenCalled();
  });
});