import '../styles/game.css';

interface QuickActionsProps {
  onAction: (command: string) => void;
  disabled: boolean;
  currentRoom: string;
}

const COMMON_ACTIONS = [
  { label: 'Look', command: 'look' },
  { label: 'Inventory', command: 'inventory' },
  { label: 'Help', command: 'help' },
];

const ROOM_ACTIONS: Record<string, Array<{ label: string; command: string }>> = {
  threshold: [
    { label: 'Talk to Traveler', command: 'talk to traveler' },
    { label: 'Go Archive', command: 'go archive' },
    { label: 'Go Cell', command: 'go keeper_cell' },
  ],
  archive: [
    { label: 'Examine Diagrams', command: 'examine technical_diagrams' },
    { label: 'Go Threshold', command: 'go threshold' },
  ],
  keeper_cell: [
    { label: 'Examine Journal', command: 'examine keeper_journal' },
    { label: 'Go Letters', command: 'go letter_room' },
    { label: 'Go Threshold', command: 'go threshold' },
  ],
  letter_room: [
    { label: 'Examine Letters', command: 'examine letter_collection' },
    { label: 'Go Back', command: 'go keeper_cell' },
  ],
  passage: [
    { label: 'Examine Doorway', command: 'examine doorway' },
    { label: 'Go Back', command: 'go archive' },
  ],
};

export function QuickActions({ onAction, disabled, currentRoom }: QuickActionsProps) {
  const roomActions = ROOM_ACTIONS[currentRoom] || [];
  const allActions = [...COMMON_ACTIONS, ...roomActions];

  return (
    <div className="quick-actions">
      {allActions.map((action) => (
        <button
          key={action.command}
          className="quick-action-btn"
          onClick={() => onAction(action.command)}
          disabled={disabled}
        >
          {action.label}
        </button>
      ))}
    </div>
  );
}
