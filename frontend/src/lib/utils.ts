/**
 * Utility functions
 */

import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Merge Tailwind CSS classes
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Format confidence score as percentage
 */
export function formatConfidence(confidence: number): string {
  return `${Math.round(confidence * 100)}%`;
}

/**
 * Get confidence color based on score
 */
export function getConfidenceColor(confidence: number): string {
  if (confidence >= 0.8) return 'text-green-600';
  if (confidence >= 0.6) return 'text-yellow-600';
  if (confidence >= 0.4) return 'text-orange-600';
  return 'text-red-600';
}

/**
 * Get confidence background color
 */
export function getConfidenceBgColor(confidence: number): string {
  if (confidence >= 0.8) return 'bg-green-100';
  if (confidence >= 0.6) return 'bg-yellow-100';
  if (confidence >= 0.4) return 'bg-orange-100';
  return 'bg-red-100';
}

/**
 * Format timestamp
 */
export function formatTime(timestamp: string): string {
  const date = new Date(timestamp);
  return date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
  });
}

/**
 * Validate email format
 */
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * Get display name from user identity
 */
export function getDisplayName(name?: string, email?: string): string {
  if (name) return name;
  if (email) return email.split('@')[0];
  return 'Guest';
}
