interface Props {
    url?: string;
    peaks?: number[];
    windows: [number, number][];
    editable: boolean;
    optional: boolean;
    showControls?: boolean;
    repeat?: boolean;
    onChangeRepeat?: (enabled: boolean) => void;
    autoplay?: boolean;
    onChangeAutoplay?: (enabled: boolean) => void;
    onEditWindow?: (window: [number, number]) => void;
    onDeleteWindow?: () => void;
    onRegionEnter?: (windowIndex: number) => void;
    onRegionLeave?: (windowIndex: number) => void;
    onRegionClick?: (windowIndex: number) => void;
}
declare const AudioViewer: ({ url, peaks, windows, editable, optional, showControls, repeat, onChangeRepeat, autoplay, onChangeAutoplay, onEditWindow, onDeleteWindow, onRegionEnter, onRegionLeave, onRegionClick, }: Props) => JSX.Element;
export default AudioViewer;
