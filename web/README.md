# VSCode Sync Tool Web Frontend

This is the web interface for the VSCode Sync Tool project.

## Features (Planned)

- User authentication (email, GitHub)
- Upload/download VSCode setup profiles
- Named profiles (e.g., "Work Laptop", "Mac Mini")
- Public sharing of setups
- Team sharing and management
- Cloud backup and restore
- Stripe integration for premium features

## Stack

- Next.js (TypeScript)
- Supabase (auth, database, storage)
- Tailwind CSS (optional, for styling)

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```
2. Set up your `.env.local` with Supabase keys:
   ```env
   NEXT_PUBLIC_SUPABASE_URL=your_project_url
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
   ```
3. Run the dev server:
   ```bash
   npm run dev
   ```

## Contributing

Pull requests and issues are welcome!
