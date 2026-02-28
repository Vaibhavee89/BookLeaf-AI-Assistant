/**
 * Confidence score indicator component
 */

import React from 'react';
import { cn, formatConfidence, getConfidenceColor, getConfidenceBgColor } from '@/lib/utils';
import { ConfidenceBreakdown } from '@/types/chat';
import { AlertCircle, CheckCircle, Info } from 'lucide-react';

interface ConfidenceIndicatorProps {
  confidence: number;
  breakdown?: ConfidenceBreakdown;
  showDetails?: boolean;
}

export const ConfidenceIndicator: React.FC<ConfidenceIndicatorProps> = ({
  confidence,
  breakdown,
  showDetails = false,
}) => {
  const [expanded, setExpanded] = React.useState(false);

  const getConfidenceIcon = (score: number) => {
    if (score >= 0.8) return <CheckCircle className="w-4 h-4" />;
    if (score >= 0.6) return <Info className="w-4 h-4" />;
    return <AlertCircle className="w-4 h-4" />;
  };

  const getConfidenceLabel = (score: number) => {
    if (score >= 0.8) return 'High Confidence';
    if (score >= 0.6) return 'Medium Confidence';
    if (score >= 0.4) return 'Low Confidence';
    return 'Very Low Confidence';
  };

  return (
    <div className="space-y-2">
      {/* Main confidence badge */}
      <div
        className={cn(
          'inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium transition-colors',
          getConfidenceBgColor(confidence),
          getConfidenceColor(confidence)
        )}
      >
        {getConfidenceIcon(confidence)}
        <span>{getConfidenceLabel(confidence)}</span>
        <span className="font-bold">{formatConfidence(confidence)}</span>
        {showDetails && breakdown && (
          <button
            onClick={() => setExpanded(!expanded)}
            className="ml-1 text-xs underline hover:no-underline"
          >
            {expanded ? 'Hide' : 'Details'}
          </button>
        )}
      </div>

      {/* Escalation warning */}
      {breakdown?.action === 'escalate' && (
        <div className="flex items-start gap-2 p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-sm">
          <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-medium text-yellow-900">Escalated to Human Agent</p>
            <p className="text-yellow-700 mt-1">
              This query has been flagged for human review due to low confidence or complexity.
            </p>
          </div>
        </div>
      )}

      {/* Detailed breakdown */}
      {expanded && breakdown && (
        <div className="p-4 bg-gray-50 rounded-lg text-sm space-y-3">
          <div>
            <h4 className="font-semibold text-gray-900 mb-2">Confidence Breakdown</h4>
            <div className="space-y-2">
              {Object.entries(breakdown.factors).map(([key, factor]) => (
                <div key={key} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="capitalize text-gray-700">{key}:</span>
                    <span className={cn('font-medium', getConfidenceColor(factor.score))}>
                      {formatConfidence(factor.score)}
                    </span>
                  </div>
                  <span className="text-gray-500 text-xs">
                    Weight: {Math.round(factor.weight * 100)}%
                  </span>
                </div>
              ))}
            </div>
          </div>

          {breakdown.weakest_factor && (
            <div className="pt-2 border-t border-gray-200">
              <p className="text-gray-600">
                <span className="font-medium">Weakest factor:</span>{' '}
                <span className="capitalize">{breakdown.weakest_factor.name}</span>{' '}
                ({formatConfidence(breakdown.weakest_factor.score)})
              </p>
            </div>
          )}

          <div className="pt-2 border-t border-gray-200">
            <p className="text-gray-600">
              <span className="font-medium">Action:</span>{' '}
              <span className={cn(
                'capitalize font-medium',
                breakdown.action === 'escalate' ? 'text-orange-600' : 'text-green-600'
              )}>
                {breakdown.action === 'escalate' ? 'Escalate to Human' : 'Auto-respond'}
              </span>
            </p>
            <p className="text-gray-500 text-xs mt-1">
              Threshold: {formatConfidence(breakdown.threshold)}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
