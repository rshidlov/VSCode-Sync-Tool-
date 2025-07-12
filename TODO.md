# TODOs for VSCode Sync Tool Project

This file tracks upcoming features, improvements, and deployment steps for both the CLI and web frontend.

## General

- [ ] Review and update project documentation (README, setup guides)
- [ ] Ensure all code (CLI and web) is linted, tested, and type-checked

## Web Frontend (Next.js)

- [ ] Customize Supabase Auth UI (branding, fields, etc.)
- [ ] Implement user dashboard after login
- [ ] Display and manage user profiles (cloud setups)
- [ ] Allow users to create, edit, and delete named profiles
- [ ] Enable public sharing of profiles via unique URLs
- [ ] Integrate with Supabase for profile CRUD operations
- [ ] Add team sharing/collaboration features
- [ ] Add payment integration (Stripe or Paddle) for premium features
- [ ] Add settings page (profile, billing, etc.)
- [ ] Add error and loading states for all async actions
- [ ] Responsive/mobile-friendly UI
- [ ] Deploy web frontend (Vercel or similar)

## CLI Tool

- [ ] Integrate CLI with cloud sync (Supabase API)
- [ ] Add commands for login/logout (auth with Supabase)
- [ ] Add commands to push/pull profiles to/from the cloud
- [ ] Add support for multiple named profiles
- [ ] Add error handling for network/cloud issues
- [ ] Add CLI tests for new cloud features

## Supabase Backend

- [ ] Finalize database schema for profiles, users, teams
- [ ] Set up RLS (Row Level Security) policies
- [ ] Add storage for profile files (settings, extensions)
- [ ] Configure GitHub OAuth for production and local dev
- [ ] Set up email/password auth
- [ ] Set up team and sharing permissions

## Deployment

- [ ] Set up production domain and SSL
- [ ] Update GitHub OAuth and Supabase settings for production
- [ ] Add CI/CD for web and CLI

---

Add new items below as needed!
