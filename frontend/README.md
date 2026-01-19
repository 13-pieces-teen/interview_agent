# Interview Agent - Web Interface

This directory contains the React + TypeScript frontend for the Interview Agent application.

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **React Dropzone** - File upload
- **Lucide React** - Icon library

## Getting Started

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

The development server will start at `http://localhost:5173`

### Build for Production

```bash
npm run build
```

The build output will be in the `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/       # React components
│   │   ├── UploadZone.tsx
│   │   ├── ResultsView.tsx
│   │   ├── ExportPanel.tsx
│   │   └── ErrorMessage.tsx
│   ├── services/         # API services
│   │   └── api.ts
│   ├── types/           # TypeScript types
│   │   └── index.ts
│   ├── App.tsx          # Main app component
│   ├── main.tsx         # Entry point
│   └── index.css        # Global styles
├── index.html           # HTML template
├── vite.config.ts       # Vite configuration
├── tailwind.config.js   # Tailwind configuration
└── package.json         # Dependencies
```

## Features

### Upload Zone
- **Text Input** - Paste interview experience text directly
- **Image Upload** - Drag & drop or select interview screenshots
- Real-time processing status

### Results View
- Structured display of interview details
- Company information and interview stage
- Questions with answers and tags
- AI-generated answer indicators

### Export Panel
- Download processed results as JSON
- Download formatted Markdown files
- Direct download links

### Options
- Toggle AI answer generation
- Choose export formats

## API Integration

The frontend communicates with the FastAPI backend via REST endpoints:

- `POST /api/process/text` - Process text content
- `POST /api/process/image` - Process image files
- `GET /api/files` - List output files
- `GET /api/download/{filename}` - Download files

API base URL is configured via the Vite proxy in development and can be set via `VITE_API_BASE` environment variable in production.

## Environment Variables

Create a `.env.local` file:

```bash
VITE_API_BASE=http://localhost:8000/api
```

## Styling

The application uses Tailwind CSS with a custom dark theme. Colors and styles can be customized in [tailwind.config.js](tailwind.config.js).

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
