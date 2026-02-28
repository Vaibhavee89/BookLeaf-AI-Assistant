# BookLeaf AI Assistant - Frontend

Modern, responsive chat interface for the BookLeaf AI Assistant built with Next.js 14, TypeScript, and Tailwind CSS.

## Features

- 🎨 **Modern UI**: Clean, professional design with Tailwind CSS
- 💬 **Real-time Chat**: Smooth chat experience with loading states
- 📊 **Confidence Indicators**: Visual feedback on AI response confidence
- 🔒 **Identity Capture**: User-friendly form for collecting user information
- 📱 **Responsive**: Works on desktop, tablet, and mobile devices
- ⚡ **Fast**: Optimized with Next.js 14 App Router
- 🎯 **TypeScript**: Full type safety throughout

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **HTTP Client**: Axios
- **State Management**: React Hooks

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend API running on `http://localhost:8000`

### Installation

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Configure environment**:
   ```bash
   cp .env.local.example .env.local
   ```

   Edit `.env.local`:
   ```bash
   NEXT_PUBLIC_API_URL=http://localhost:8000
   NEXT_PUBLIC_APP_NAME=BookLeaf AI Assistant
   ```

3. **Start development server**:
   ```bash
   npm run dev
   ```

4. **Open browser**:
   Navigate to [http://localhost:3000](http://localhost:3000)

### Build for Production

```bash
npm run build
npm start
```

## Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── chat/page.tsx      # Main chat page
│   │   ├── layout.tsx         # Root layout
│   │   ├── page.tsx           # Home (redirects to chat)
│   │   └── globals.css        # Global styles
│   ├── components/
│   │   └── chat/              # Chat components
│   │       ├── ChatContainer.tsx       # Main container
│   │       ├── ChatMessage.tsx         # Message bubble
│   │       ├── ChatInput.tsx           # Input field
│   │       ├── ConfidenceIndicator.tsx # Confidence display
│   │       └── IdentityForm.tsx        # Identity capture
│   ├── hooks/
│   │   └── useChat.ts         # Chat logic hook
│   ├── lib/
│   │   ├── api-client.ts      # Backend API client
│   │   └── utils.ts           # Utility functions
│   └── types/
│       └── chat.ts            # TypeScript types
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.js
```

## Components

### ChatContainer
Main chat interface component that orchestrates the entire chat experience.

**Features**:
- Message display with auto-scroll
- Loading indicators
- Error handling
- Confidence score display
- Conversation reset

### ChatMessage
Individual message bubble component.

**Props**:
- `message`: Message object with role, content, timestamp
- `showTimestamp`: Whether to show timestamp

**Features**:
- Role-based styling (user vs assistant)
- Avatar icons
- Timestamp display
- Intent labels

### ChatInput
Message input field with send button.

**Props**:
- `onSendMessage`: Callback for sending messages
- `disabled`: Loading state
- `placeholder`: Input placeholder text

**Features**:
- Auto-resize textarea
- Enter to send (Shift+Enter for new line)
- Loading state handling
- Disabled state styling

### ConfidenceIndicator
Visual confidence score display with breakdown.

**Props**:
- `confidence`: Overall confidence score (0-1)
- `breakdown`: Detailed confidence factors
- `showDetails`: Toggle details view

**Features**:
- Color-coded badges (green/yellow/orange/red)
- Expandable factor breakdown
- Escalation warnings
- Threshold display

### IdentityForm
User information capture form.

**Props**:
- `onSubmit`: Callback with user identity

**Features**:
- Field validation
- Email format validation
- Optional phone field
- Clear error messages

## Hooks

### useChat
Custom hook for managing chat state and API communication.

**Returns**:
- `messages`: Array of messages
- `isLoading`: Loading state
- `error`: Error message
- `conversationId`: Current conversation ID
- `lastResponse`: Last API response with metadata
- `sendMessage`: Function to send messages
- `clearError`: Function to clear error
- `resetChat`: Function to reset conversation

**Usage**:
```typescript
const {
  messages,
  isLoading,
  sendMessage,
} = useChat(userIdentity);
```

## API Integration

The frontend communicates with the FastAPI backend through the `apiClient`:

```typescript
import { apiClient } from '@/lib/api-client';

// Send message
const response = await apiClient.sendMessage({
  message: "Hello!",
  name: "John Doe",
  email: "john@example.com",
});

// Get conversation
const conversation = await apiClient.getConversation(conversationId);

// Get escalations
const escalations = await apiClient.getEscalations();
```

## Styling

### Tailwind Configuration
Custom color palette with primary blue theme:

```typescript
colors: {
  primary: {
    50: '#f0f9ff',
    500: '#0ea5e9',
    600: '#0284c7',
    // ...
  },
}
```

### Responsive Design
- Mobile-first approach
- Breakpoints: `sm`, `md`, `lg`, `xl`, `2xl`
- Flexible layouts with Flexbox and Grid

### Custom Styles
- Smooth scrolling
- Custom scrollbar styling
- Focus states for accessibility
- Loading animations

## Type Safety

Full TypeScript coverage with interfaces for:
- `Message`: Chat message structure
- `ChatResponse`: API response structure
- `ConfidenceBreakdown`: Confidence score details
- `UserIdentity`: User information
- `ChatRequest`: API request structure

## Development

### Code Style
- ESLint for linting
- Prettier for formatting
- TypeScript strict mode

### Type Checking
```bash
npm run type-check
```

### Linting
```bash
npm run lint
```

## Troubleshooting

### Backend Connection Issues
**Problem**: "No response from server"

**Solution**:
1. Verify backend is running on `http://localhost:8000`
2. Check `NEXT_PUBLIC_API_URL` in `.env.local`
3. Verify CORS is enabled in backend

### Build Errors
**Problem**: TypeScript errors during build

**Solution**:
```bash
npm run type-check
```
Fix reported type errors

### Styling Issues
**Problem**: Tailwind classes not applied

**Solution**:
1. Restart dev server
2. Check `tailwind.config.ts` paths
3. Verify `@tailwind` directives in `globals.css`

## Performance Optimization

- **Code Splitting**: Automatic with Next.js
- **Image Optimization**: Next.js Image component
- **Font Optimization**: Next.js Font optimization
- **Client-side Caching**: React Query (can be added)
- **API Response Caching**: Axios cache adapter (optional)

## Accessibility

- Semantic HTML elements
- ARIA labels for interactive elements
- Keyboard navigation support
- Focus indicators
- Screen reader friendly

## Future Enhancements

- [ ] Real-time updates with WebSockets
- [ ] Message search functionality
- [ ] Conversation history sidebar
- [ ] Dark mode support
- [ ] File upload capability
- [ ] Voice input
- [ ] Message reactions
- [ ] Export conversation
- [ ] Multi-language support

## Contributing

1. Follow TypeScript best practices
2. Use functional components with hooks
3. Add proper TypeScript types
4. Test responsive design
5. Ensure accessibility compliance

## License

Part of the BookLeaf Publishing AI Assistant project.
