import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import AnnotationCard from "./AnnotationCard";

const { importWhiteboxStateStore } = Whitebox;
const { getClasses } = Whitebox.utils;
const { mockWhiteboxStateStore, resetWhiteboxStateStoreMocks } = WhiteboxTest;

const annotationData = {
  author_name: "ATC",
  message: "Possible pilot deviation",
  timestamp: "2024-01-01T00:00:42.000Z",
  avatar_initial: "A",
};

const flightSessionData = {
  started_at: "2024-01-01T00:00:00.000Z",
  ended_at: "2024-01-01T01:00:00.000Z",
};

const renderCard = (moreProps = {}) => {
  const props = {
    annotation: annotationData,
    flightSession: flightSessionData,
    ...moreProps,
  };
  return render(<AnnotationCard {...props} />);
};

describe("AnnotationCard", () => {
  beforeEach(async () => {
    vi.resetModules();

    mockWhiteboxStateStore("flight.mission-control", {
      setPlaybackTime: vi.fn(),
    });

    globalThis.Whitebox.utils = {
      getClasses,
      humanize: {
        formatDuration: vi.fn().mockReturnValue("00:42"),
      }
    };
  })

  afterEach(() => {
    resetWhiteboxStateStoreMocks();
  })

  it("renders author, message, timestamp text, and Avatar", () => {
    renderCard({status: "current"});

    expect(screen.getByText("ATC")).toBeInTheDocument();
    expect(screen.getByText("Possible pilot deviation")).toBeInTheDocument();
    expect(screen.getByText("00:42")).toBeInTheDocument();

    // formatDuration called with started_at and annotation.timestamp
    const mockFormatDuration = globalThis.Whitebox.utils.humanize.formatDuration;
    expect(mockFormatDuration).toHaveBeenCalledTimes(1);
    const [startArg, tsArg] = mockFormatDuration.mock.calls[0];
    expect(startArg).toBeInstanceOf(Date);
    expect(tsArg).toBeInstanceOf(Date);
    expect(startArg.toISOString()).toBe("2024-01-01T00:00:00.000Z");
    expect(tsArg.toISOString()).toBe("2024-01-01T00:00:42.000Z");
  });

  it("applies styling based on status=past", () => {
    const { container } = renderCard({ status: "past" });
    const root = container.firstChild;
    expect(root).toHaveClass("border-medium-emphasis");
  });

  it("applies styling based on status=current", () => {
    const { container } = renderCard({ status: "current" });
    const root = container.firstChild;
    expect(root).toHaveClass("border-high-emphasis");
  });

  it("applies styling based on status=upcoming", () => {
    const { container } = renderCard({ status: "upcoming" });
    const root = container.firstChild;
    expect(root).toHaveClass("border-low-emphasis");
    expect(root).toHaveClass("opacity-60");
  });

  it("clicking timestamp sets playback time when flightSession has ended_at", async () => {
    const useMissionControlStore = importWhiteboxStateStore("flight.mission-control");
    const mockSetPlaybackTime = useMissionControlStore((state) => state.setPlaybackTime);

    renderCard({
      status: "current",
      flightSession: { ...flightSessionData, ended_at: "2024-01-01T01:00:00.000Z" },
    });

    await userEvent.click(screen.getByText("00:42"));

    expect(mockSetPlaybackTime).toHaveBeenCalledTimes(1);
    const [dt, flag] = mockSetPlaybackTime.mock.calls[0];
    expect(dt).toBeInstanceOf(Date);
    expect(dt.toISOString()).toBe("2024-01-01T00:00:42.000Z");
    expect(flag).toBe(true);
  });

  it("clicking timestamp does nothing during active session (no ended_at)", async () => {
    const useMissionControlStore = importWhiteboxStateStore("flight.mission-control");
    const mockSetPlaybackTime = useMissionControlStore((state) => state.setPlaybackTime);

    renderCard({
      status: "current",
      flightSession: { ...flightSessionData, ended_at: null },
    });

    await userEvent.click(screen.getByText("00:42"));
    expect(mockSetPlaybackTime).not.toHaveBeenCalled();
  });
});