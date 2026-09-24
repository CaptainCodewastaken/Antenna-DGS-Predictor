import React from 'react';
import './Layout.css';
import { Sidebar } from './Sidebar';
import { useAntennaConfig } from '../../hooks/useAntennaConfig';

interface LayoutProps {
  children: (config: ReturnType<typeof useAntennaConfig>['config']) => React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { config, updateSubstrate, updatePatch, updateFeed, addSlot, removeSlot, updateSlot } = useAntennaConfig();

  return (
    <div className="layout-container">
      <Sidebar 
        config={config}
        updateSubstrate={updateSubstrate}
        updatePatch={updatePatch}
        updateFeed={updateFeed}
        addSlot={addSlot}
        removeSlot={removeSlot}
        updateSlot={updateSlot}
      />
      <div className="layout-main">
        {children(config)}
      </div>
    </div>
  );
};
