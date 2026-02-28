/**
 * Identity capture form component
 */

import React, { useState } from 'react';
import { cn, isValidEmail } from '@/lib/utils';
import { UserIdentity } from '@/types/chat';
import { User, Mail, Phone } from 'lucide-react';

interface IdentityFormProps {
  onSubmit: (identity: UserIdentity) => void;
}

export const IdentityForm: React.FC<IdentityFormProps> = ({ onSubmit }) => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!name.trim()) {
      newErrors.name = 'Name is required';
    }

    if (!email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!isValidEmail(email)) {
      newErrors.email = 'Invalid email format';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (validate()) {
      onSubmit({
        name: name.trim(),
        email: email.trim(),
        phone: phone.trim() || undefined,
      });
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 p-4">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-100 rounded-full mb-4">
              <User className="w-8 h-8 text-primary-600" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              Welcome to BookLeaf AI Assistant
            </h1>
            <p className="text-gray-600">
              Please provide your information to get started
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Name field */}
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                Full Name *
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  id="name"
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className={cn(
                    'w-full pl-10 pr-4 py-3 rounded-lg border',
                    'focus:outline-none focus:ring-2 focus:ring-primary-500',
                    errors.name ? 'border-red-300' : 'border-gray-300'
                  )}
                  placeholder="Sarah Johnson"
                />
              </div>
              {errors.name && (
                <p className="mt-1 text-sm text-red-600">{errors.name}</p>
              )}
            </div>

            {/* Email field */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                Email Address *
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className={cn(
                    'w-full pl-10 pr-4 py-3 rounded-lg border',
                    'focus:outline-none focus:ring-2 focus:ring-primary-500',
                    errors.email ? 'border-red-300' : 'border-gray-300'
                  )}
                  placeholder="sarah.johnson@email.com"
                />
              </div>
              {errors.email && (
                <p className="mt-1 text-sm text-red-600">{errors.email}</p>
              )}
            </div>

            {/* Phone field (optional) */}
            <div>
              <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-2">
                Phone Number (Optional)
              </label>
              <div className="relative">
                <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  id="phone"
                  type="tel"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  className={cn(
                    'w-full pl-10 pr-4 py-3 rounded-lg border border-gray-300',
                    'focus:outline-none focus:ring-2 focus:ring-primary-500'
                  )}
                  placeholder="+1-555-0101"
                />
              </div>
            </div>

            {/* Submit button */}
            <button
              type="submit"
              className={cn(
                'w-full py-3 px-4 rounded-lg font-medium',
                'bg-primary-500 text-white',
                'hover:bg-primary-600 active:bg-primary-700',
                'transition-colors duration-200',
                'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2'
              )}
            >
              Start Chatting
            </button>
          </form>

          {/* Footer note */}
          <p className="mt-6 text-xs text-center text-gray-500">
            Your information is used to provide personalized support and is kept confidential.
          </p>
        </div>
      </div>
    </div>
  );
};
