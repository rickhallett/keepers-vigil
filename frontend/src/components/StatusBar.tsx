import { useState } from 'react';
import '../styles/game.css';

interface StatusBarProps {
  currentRoom: string;
  inventory: string[];
  exits: string[];
}

const ROOM_NAMES: Record<string, string> = {
  threshold: 'The Threshold',
  keeper_cell: "The Keeper's Cell",
  archive: 'The Archive',
  letter_room: 'The Letter Room',
  passage: 'The Passage',
};

export function StatusBar({ currentRoom, inventory, exits }: StatusBarProps) {
  const [collapsed, setCollapsed] = useState(false);
  const roomName = ROOM_NAMES[currentRoom] || currentRoom;
  const exitNames = exits.map(e => ROOM_NAMES[e] || e);

  return (
    <div className={`status-bar ${collapsed ? 'collapsed' : ''}`}>
      <div className="status-room">
        <span className="status-label">Location:</span>
        <span className="status-value">{roomName}</span>
      </div>

      {!collapsed && (
        <>
          <div className="status-exits">
            <span className="status-label">Exits:</span>
            <span className="status-value">{exitNames.join(', ') || 'none'}</span>
          </div>

          {inventory.length > 0 && (
            <div className="status-inventory">
              <span className="status-label">Carrying:</span>
              <span className="status-value">{inventory.join(', ')}</span>
            </div>
          )}
        </>
      )}

      <button
        className="status-toggle"
        onClick={() => setCollapsed(!collapsed)}
        aria-label={collapsed ? 'Expand status bar' : 'Collapse status bar'}
      >
        {collapsed ? '▼' : '▲'}
      </button>
    </div>
  );
}
