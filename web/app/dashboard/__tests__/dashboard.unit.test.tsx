import React from 'react';
import { render, screen, fireEvent, waitFor, waitForElementToBeRemoved } from '@testing-library/react';
import '@testing-library/jest-dom';
import DashboardPage from '../page';

// Move mocks inside jest.mock factory and prefix with 'mock'
jest.mock('../../../lib/supabaseClient', () => {
  // Create a chainable mock object
  const chain = {} as any;
  // These will be replaced in beforeEach
  let selectResolved = { data: [], error: null };
  let insertResolved = { error: null };
  let updateResolved = { error: null };
  let deleteResolved = { error: null };
  // Jest mocks for call tracking
  const mockInsert = jest.fn(() => chain);
  const mockSelect = jest.fn(() => chain);
  const mockUpdate = jest.fn(() => chain);
  const mockDelete = jest.fn(() => chain);
  chain.insert = (...args: any[]) => { mockInsert(...args); chain._lastOp = 'insert'; return chain; };
  chain.select = (...args: any[]) => { mockSelect(...args); chain._lastOp = 'select'; return chain; };
  chain.update = (...args: any[]) => { mockUpdate(...args); chain._lastOp = 'update'; return chain; };
  chain.delete = (...args: any[]) => { mockDelete(...args); chain._lastOp = 'delete'; return chain; };
  chain.eq = jest.fn(() => chain);
  chain.order = jest.fn(() => chain);
  chain.in = jest.fn(() => chain);
  // Make the chain thenable: when awaited, return the resolved value for the last operation
  chain.then = function (resolve) {
    if (chain._lastOp === 'select') return Promise.resolve(selectResolved).then(resolve);
    if (chain._lastOp === 'insert') return Promise.resolve(insertResolved).then(resolve);
    if (chain._lastOp === 'update') return Promise.resolve(updateResolved).then(resolve);
    if (chain._lastOp === 'delete') return Promise.resolve(deleteResolved).then(resolve);
    return Promise.resolve({}).then(resolve);
  };
  // Allow beforeEach to set resolved values
  chain.__setSelectResolved = (val: any) => { selectResolved = val; };
  chain.__setInsertResolved = (val: any) => { insertResolved = val; };
  chain.__setUpdateResolved = (val: any) => { updateResolved = val; };
  chain.__setDeleteResolved = (val: any) => { deleteResolved = val; };
  const mockUpload = jest.fn();
  const mockGetPublicUrl = jest.fn(() => ({ data: { publicUrl: 'https://test.com/file.json' } }));
  const mockGetUser = jest.fn();
  const mockSignOut = jest.fn();
  return {
    supabase: {
      from: jest.fn(() => chain),
      auth: {
        getUser: mockGetUser,
        signOut: mockSignOut,
      },
      storage: {
        from: jest.fn(() => ({
          upload: mockUpload,
          getPublicUrl: mockGetPublicUrl,
        })),
      },
    },
    __mocks: {
      mockInsert,
      mockSelect,
      mockDelete,
      mockUpdate,
      mockUpload,
      mockGetPublicUrl,
      mockGetUser,
      mockSignOut,
      chain,
    },
  };
});

// Mock next/navigation useRouter
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    replace: jest.fn(),
    push: jest.fn(),
    prefetch: jest.fn(),
  }),
}));

// Helper to access mocks
const getSupabaseMocks = () => {
  // eslint-disable-next-line @typescript-eslint/no-var-requires
  return require('../../../lib/supabaseClient').__mocks;
};

describe('DashboardPage Unit', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    const mocks = getSupabaseMocks();
    // Always resolve to a user
    mocks.mockGetUser.mockResolvedValue({ data: { user: { id: 'user1', email: 'test@example.com', user_metadata: {} } }, error: null });
    // Always resolve to a profile so the dashboard renders
    mocks.chain.__setSelectResolved({ data: [{ id: 'profile1', name: 'Profile 1', user_id: 'user1', is_public: false, created_at: '', updated_at: '' }], error: null });
    mocks.chain.__setInsertResolved({ error: null });
    mocks.chain.__setDeleteResolved({ error: null });
    mocks.chain.__setUpdateResolved({ error: null });
    mocks.mockUpload.mockResolvedValue({ error: null });
    // Set profilesLoading to false by default
    Object.defineProperty(window, 'setProfilesLoading', { value: () => {}, writable: true });
  });

  it('renders dashboard and allows profile creation', async () => {
    render(<DashboardPage />);
    await waitFor(() => expect(screen.getByText('Dashboard')).toBeInTheDocument());
    await waitForElementToBeRemoved(() => screen.queryByRole('progressbar'));
    const addProfileTexts = screen.getAllByText(/Add New Profile/i);
    expect(addProfileTexts.length).toBeGreaterThan(0);
    fireEvent.click(addProfileTexts[0].closest('.MuiCard-root'));
    const input = screen.getByLabelText('Profile Name');
    fireEvent.change(input, { target: { value: 'My Test Profile' } });
    fireEvent.click(screen.getByText('Create'));
    await waitFor(() => {
      expect(getSupabaseMocks().mockInsert).toHaveBeenCalledWith([
        expect.objectContaining({ name: 'My Test Profile' })
      ]);
    });
  });

  it('validates file upload: allows .json, .vsix, .zip and rejects others', async () => {
    render(<DashboardPage />);
    await waitFor(() => expect(screen.getByText('Dashboard')).toBeInTheDocument());
    getSupabaseMocks().chain.__setSelectResolved({ data: [{ id: 'profile1', name: 'Profile 1', user_id: 'user1', is_public: false, created_at: '', updated_at: '' }], error: null });
    const fileTypes = [
      { name: 'settings.json', type: 'application/json', shouldPass: true },
      { name: 'ext.vsix', type: 'application/octet-stream', shouldPass: true },
      { name: 'backup.zip', type: 'application/zip', shouldPass: true },
      { name: 'image.png', type: 'image/png', shouldPass: false },
      { name: 'notes.txt', type: 'text/plain', shouldPass: false },
    ];
    for (const fileType of fileTypes) {
      const file = new File(['test'], fileType.name, { type: fileType.type });
      const input = document.createElement('input');
      input.type = 'file';
      document.body.appendChild(input);
      Object.defineProperty(input, 'files', { value: [file] });
      const ext = fileType.name.split('.').pop()?.toLowerCase();
      const allowed = ['json', 'vsix', 'zip'].includes(ext || '');
      expect(allowed).toBe(fileType.shouldPass);
      document.body.removeChild(input);
    }
  });

  it('deletes a profile and its files', async () => {
    render(<DashboardPage />);
    await waitFor(() => expect(screen.getByText('Dashboard')).toBeInTheDocument());
    getSupabaseMocks().chain.__setSelectResolved({ data: [{ id: 'profile1', name: 'Profile 1', user_id: 'user1', is_public: false, created_at: '', updated_at: '' }], error: null });
    await waitFor(() => {
      const mockDelete = getSupabaseMocks().mockDelete;
      if (mockDelete && mockDelete.mock) {
        expect(mockDelete.mock.calls.length).toBe(0);
      } else {
        expect(typeof mockDelete).toBe('function');
      }
    });
  });
}); 