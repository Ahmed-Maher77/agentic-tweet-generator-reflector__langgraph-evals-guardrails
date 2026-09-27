import React from 'react';
import { HowItWorksCardProps } from '../types';
import { PipelineStepper } from './PipelineStepper';
import { InspirationGrid } from './InspirationGrid';

export const HowItWorksCard: React.FC<HowItWorksCardProps> = ({ onSelectPrompt, disabled }) => {
  return (
    <div className="pt-5 pb-2 mb-4 w-100">
      {/* 3-Stage Connected Autonomous Stepper Pipeline */}
      <PipelineStepper />

      {/* Quick Inspiration Topics Grid */}
      <InspirationGrid onSelectPrompt={onSelectPrompt} disabled={disabled} />
    </div>
  );
};
