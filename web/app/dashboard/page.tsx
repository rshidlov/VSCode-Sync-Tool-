'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { supabase } from '../../lib/supabaseClient';
import type { AuthUser } from '@supabase/supabase-js';
import {
  Box, Button, Card, CardContent, CardActions, Typography, Grid, Avatar, IconButton, TextField, Tooltip, CircularProgress
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import InsertDriveFileIcon from '@mui/icons-material/InsertDriveFile';
import DescriptionIcon from '@mui/icons-material/Description';
import ExtensionIcon from '@mui/icons-material/Extension';
import ArchiveIcon from '@mui/icons-material/Archive';
import EditIcon from '@mui/icons-material/Edit';
import SaveIcon from '@mui/icons-material/Save';
import CancelIcon from '@mui/icons-material/Cancel';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline';
import DeleteIcon from '@mui/icons-material/Delete';
import DialogContentText from '@mui/material/DialogContentText';

interface Profile {
  id: string;
  name: string;
  is_public: boolean;
  created_at: string;
  updated_at: string;
}

interface FileEntry {
  id: string;
  profile_id: string;
  file_url: string;
  created_at: string;
}

function isValidVSCodeSettings(json: any): boolean {
  // Accept plain VSCode settings object
  const looksLikeVSCodeSettings = (obj: any) =>
    typeof obj === 'object' &&
    obj !== null &&
    (
      'editor.fontSize' in obj ||
      'workbench.colorTheme' in obj ||
      'files.autoSave' in obj
    );
  // Accept CLI-exported object with a 'settings' property
  if (looksLikeVSCodeSettings(json)) return true;
  if (
    typeof json === 'object' &&
    json !== null &&
    'settings' in json &&
    looksLikeVSCodeSettings(json.settings)
  ) {
    return true;
  }
  return false;
}

function getFileTypeIcon(ext: string) {
  switch (ext) {
    case 'json':
      return <DescriptionIcon color="primary" fontSize="large" />;
    case 'vsix':
      return <ExtensionIcon color="secondary" fontSize="large" />;
    case 'zip':
      return <ArchiveIcon color="action" fontSize="large" />;
    default:
      return <InsertDriveFileIcon color="disabled" fontSize="large" />;
  }
}

function getInitials(name: string) {
  return name.split(' ').map(n => n[0]).join('').toUpperCase();
}

// Helper component for file card meta
function FileCard({ file }: { file: FileEntry }) {
  const ext = file.file_url.split('.').pop()?.toLowerCase();
  const [meta, setMeta] = useState<{ settings: number; extensions: number } | null>(null);
  useEffect(() => {
    if (ext === 'json') {
      fetch(file.file_url)
        .then(res => res.json())
        .then(json => {
          if (json && typeof json === 'object') {
            if ('settings' in json && typeof json.settings === 'object') {
              setMeta({
                settings: Object.keys(json.settings).length,
                extensions: Array.isArray(json.extensions) ? json.extensions.length : 0,
              });
            } else {
              setMeta({
                settings: Object.keys(json).length,
                extensions: 0,
              });
            }
          }
        })
        .catch(() => setMeta(null));
    }
  }, [file.file_url]);
  return (
    <Card variant="outlined" sx={{ borderRadius: 2, boxShadow: 1, p: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
      {getFileTypeIcon(ext || '')}
      <Box flex={1}>
        <Typography fontWeight={500} noWrap>{file.file_url.split('/').pop()}</Typography>
        <Typography variant="caption" color="text.secondary">{new Date(file.created_at).toLocaleString()}</Typography>
        {ext === 'json' && meta && (
          <Typography variant="caption" color="primary" display="block">
            {meta.settings} settings{meta.extensions ? `, ${meta.extensions} extensions` : ''}
          </Typography>
        )}
      </Box>
      <Button href={file.file_url} target="_blank" rel="noopener noreferrer" variant="contained" size="small">Download</Button>
    </Card>
  );
}

export default function DashboardPage() {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [profilesLoading, setProfilesLoading] = useState(true);
  const [profilesError, setProfilesError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const [filesByProfile, setFilesByProfile] = useState<Record<string, FileEntry[]>>({});
  const [fileUploadLoading, setFileUploadLoading] = useState<string | null>(null); // profile_id
  const [fileUploadError, setFileUploadError] = useState<string | null>(null);
  const [editingProfileId, setEditingProfileId] = useState<string | null>(null);
  const [profileNameInput, setProfileNameInput] = useState<string>('');
  const [avatarUrl, setAvatarUrl] = useState<string | null>(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [newProfileName, setNewProfileName] = useState('');
  const [creatingProfile, setCreatingProfile] = useState(false);
  const [createProfileError, setCreateProfileError] = useState<string | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [profileToDelete, setProfileToDelete] = useState<Profile | null>(null);
  const [deletingProfile, setDeletingProfile] = useState(false);
  const [deleteProfileError, setDeleteProfileError] = useState<string | null>(null);

  useEffect(() => {
    const getUser = async () => {
      const { data, error } = await supabase.auth.getUser();
      if (error || !data.user) {
        router.replace('/auth');
      } else {
        setUser(data.user);
      }
      setLoading(false);
    };
    getUser();
  }, [router]);

  useEffect(() => {
    const fetchProfiles = async () => {
      if (!user) return;
      setProfilesLoading(true);
      setProfilesError(null);
      const { data, error } = await supabase
        .from('profiles')
        .select('*')
        .eq('user_id', user.id)
        .order('created_at', { ascending: false });
      if (error) {
        setProfilesError(error.message);
        setProfilesLoading(false);
        return;
      }
      if ((data || []).length === 0) {
        // Auto-create a default profile for new users
        const { error: createError } = await supabase.from('profiles').insert([
          {
            user_id: user.id,
            name: 'My profile',
            is_public: false,
          },
        ]);
        if (createError) {
          setProfilesError('Failed to auto-create profile: ' + createError.message);
          setProfilesLoading(false);
          return;
        }
        // Refetch profiles after creation
        const { data: newData, error: newError } = await supabase
          .from('profiles')
          .select('*')
          .eq('user_id', user.id)
          .order('created_at', { ascending: false });
        if (newError) {
          setProfilesError(newError.message);
        } else {
          setProfiles(newData || []);
        }
        setProfilesLoading(false);
        return;
      }
      setProfiles(data || []);
      setProfilesLoading(false);
    };
    if (user) {
      fetchProfiles();
    }
  }, [user]);

  // Fetch files for all profiles
  useEffect(() => {
    const fetchFiles = async () => {
      if (!profiles.length) return;
      const profileIds = profiles.map((p) => p.id);
      const { data, error } = await supabase
        .from('files')
        .select('*')
        .in('profile_id', profileIds);
      if (!error && data) {
        const grouped: Record<string, FileEntry[]> = {};
        for (const file of data) {
          if (!grouped[file.profile_id]) grouped[file.profile_id] = [];
          grouped[file.profile_id].push(file);
        }
        setFilesByProfile(grouped);
      }
    };
    if (profiles.length) fetchFiles();
  }, [profiles]);

  // Fetch GitHub avatar if available
  useEffect(() => {
    if (user && user.user_metadata && user.user_metadata.avatar_url) {
      setAvatarUrl(user.user_metadata.avatar_url);
    } else {
      setAvatarUrl(null);
    }
  }, [user]);

  const handleFileUpload = async (profileId: string, file: File) => {
    console.log('Uploading for profileId:', profileId, 'userId:', user?.id);
    setFileUploadLoading(profileId);
    setFileUploadError(null);
    const ext = file.name.split('.').pop()?.toLowerCase();
    if (ext === 'json') {
      // Validate JSON
      try {
        const text = await file.text();
        const json = JSON.parse(text);
        if (!isValidVSCodeSettings(json)) {
          setFileUploadError('Invalid VSCode settings.json file.');
          setFileUploadLoading(null);
          return;
        }
      } catch {
        setFileUploadError('Invalid JSON file.');
        setFileUploadLoading(null);
        return;
      }
    } else if (ext === 'vsix') {
      // Optionally: add more checks for vsix
    } else {
      setFileUploadError('Only .json (VSCode settings) and .vsix files are allowed.');
      setFileUploadLoading(null);
      return;
    }
    // Upload to Supabase Storage
    const filePath = `${profileId}/${Date.now()}_${file.name}`;
    const { error: uploadError } = await supabase.storage.from('data').upload(filePath, file, { upsert: false });
    if (uploadError) {
      setFileUploadError('Failed to upload file: ' + uploadError.message);
      setFileUploadLoading(null);
      return;
    }
    // Get public URL (or signed URL if private)
    const { data: urlData } = supabase.storage.from('data').getPublicUrl(filePath);
    const fileUrl = urlData?.publicUrl || '';
    // Insert into files table
    const { error: insertError } = await supabase.from('files').insert([
      {
        profile_id: profileId,
        file_url: fileUrl,
      },
    ]);
    if (insertError) {
      setFileUploadError('Failed to save file record: ' + insertError.message);
      setFileUploadLoading(null);
      return;
    }
    // Refresh files
    setFileUploadLoading(null);
    setFileUploadError(null);
    // Refetch files for this profile
    const { data: newFiles } = await supabase
      .from('files')
      .select('*')
      .eq('profile_id', profileId);
    setFilesByProfile((prev) => ({ ...prev, [profileId]: newFiles || [] }));
  };

  const handleProfileNameEdit = (profile: Profile) => {
    setEditingProfileId(profile.id);
    setProfileNameInput(profile.name);
  };

  const handleProfileNameSave = async (profile: Profile) => {
    if (profileNameInput.trim() && profileNameInput !== profile.name) {
      await supabase.from('profiles').update({ name: profileNameInput.trim() }).eq('id', profile.id);
      setProfiles(profiles.map(p => p.id === profile.id ? { ...p, name: profileNameInput.trim() } : p));
    }
    setEditingProfileId(null);
  };

  const handleCreateProfile = async () => {
    if (!newProfileName.trim()) return;
    setCreatingProfile(true);
    setCreateProfileError(null);
    const { error } = await supabase.from('profiles').insert([
      {
        user_id: user?.id,
        name: newProfileName.trim(),
        is_public: false,
      },
    ]);
    setCreatingProfile(false);
    if (error) {
      setCreateProfileError(error.message);
      return;
    }
    setCreateDialogOpen(false);
    setNewProfileName('');
    // Refetch profiles
    const { data, error: fetchError } = await supabase
      .from('profiles')
      .select('*')
      .eq('user_id', user?.id)
      .order('created_at', { ascending: false });
    if (!fetchError && data) setProfiles(data);
  };

  const handleDeleteProfile = async () => {
    if (!profileToDelete) return;
    setDeletingProfile(true);
    setDeleteProfileError(null);
    // Delete files associated with the profile first
    await supabase.from('files').delete().eq('profile_id', profileToDelete.id);
    // Then delete the profile
    const { error } = await supabase.from('profiles').delete().eq('id', profileToDelete.id);
    setDeletingProfile(false);
    if (error) {
      setDeleteProfileError(error.message);
      return;
    }
    setDeleteDialogOpen(false);
    setProfileToDelete(null);
    // Refetch profiles
    const { data, error: fetchError } = await supabase
      .from('profiles')
      .select('*')
      .eq('user_id', user?.id)
      .order('created_at', { ascending: false });
    if (!fetchError && data) setProfiles(data);
  };

  const handleLogout = async () => {
    await supabase.auth.signOut();
    router.replace('/auth');
  };

  if (loading) {
    return <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh"><CircularProgress /></Box>;
  }

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#f5f7fa', p: 3 }}>
      <Box display="flex" alignItems="center" justifyContent="space-between" mb={4}>
        <Typography variant="h4" fontWeight={700}>Dashboard</Typography>
        <Box display="flex" alignItems="center" gap={2}>
          {avatarUrl ? (
            <Avatar src={avatarUrl} alt="User avatar" />
          ) : (
            <Avatar>{user?.user_metadata?.full_name ? getInitials(user.user_metadata.full_name) : (user?.email?.[0] || '?')}</Avatar>
          )}
          <Button variant="outlined" color="secondary" onClick={handleLogout}>Log out</Button>
        </Box>
      </Box>
      {/* Create Profile Dialog */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)}>
        <DialogTitle>Create New Profile</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Profile Name"
            fullWidth
            value={newProfileName}
            onChange={e => setNewProfileName(e.target.value)}
            disabled={creatingProfile}
            error={!!createProfileError}
            helperText={createProfileError}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)} disabled={creatingProfile}>Cancel</Button>
          <Button onClick={handleCreateProfile} variant="contained" disabled={creatingProfile || !newProfileName.trim()}>
            {creatingProfile ? <CircularProgress size={20} /> : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
      {/* Delete Profile Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Delete Profile</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete the profile "{profileToDelete?.name}"? This will also delete all files associated with this profile. This action cannot be undone.
          </DialogContentText>
          {deleteProfileError && <Typography color="error" mt={2}>{deleteProfileError}</Typography>}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)} disabled={deletingProfile}>Cancel</Button>
          <Button onClick={handleDeleteProfile} color="error" variant="contained" disabled={deletingProfile}>
            {deletingProfile ? <CircularProgress size={20} /> : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>
      <Grid container spacing={3}>
        {profilesLoading ? (
          <Grid item xs={12}><CircularProgress /></Grid>
        ) : profilesError ? (
          <Grid item xs={12}><Typography color="error">{profilesError}</Typography></Grid>
        ) : profiles.length === 0 ? (
          <Grid item xs={12}><Typography>No profiles found. Create your first one!</Typography></Grid>
        ) : (
          <>
            {profiles.map((profile) => (
              <Grid item xs={12} md={6} lg={4} key={profile.id}>
                <Card sx={{ borderRadius: 3, boxShadow: 3, minHeight: 320, display: 'flex', flexDirection: 'column' }}>
                  <CardContent>
                    <Box display="flex" alignItems="center" justifyContent="space-between">
                      {editingProfileId === profile.id ? (
                        <TextField
                          value={profileNameInput}
                          onChange={e => setProfileNameInput(e.target.value)}
                          size="small"
                          sx={{ flex: 1, mr: 1 }}
                          autoFocus
                        />
                      ) : (
                        <Typography variant="h6" fontWeight={600}>{profile.name}</Typography>
                      )}
                      <Box display="flex" alignItems="center">
                        {editingProfileId === profile.id ? (
                          <>
                            <IconButton onClick={() => handleProfileNameSave(profile)} color="primary"><SaveIcon /></IconButton>
                            <IconButton onClick={() => setEditingProfileId(null)} color="error"><CancelIcon /></IconButton>
                          </>
                        ) : (
                          <>
                            <Tooltip title="Edit profile name"><IconButton onClick={() => handleProfileNameEdit(profile)}><EditIcon /></IconButton></Tooltip>
                            <Tooltip title="Delete profile">
                              <IconButton color="error" onClick={() => { setProfileToDelete(profile); setDeleteDialogOpen(true); }}>
                                <DeleteIcon />
                              </IconButton>
                            </Tooltip>
                          </>
                        )}
                      </Box>
                    </Box>
                    <Typography variant="body2" color="text.secondary" mb={1}>{new Date(profile.created_at).toLocaleString()}</Typography>
                    <Box mt={2}>
                      <Grid container spacing={2}>
                        {(filesByProfile[profile.id] || []).map(file => (
                          <Grid item xs={12} key={file.id}>
                            <FileCard file={file} />
                          </Grid>
                        ))}
                        {/* Add new file card */}
                        <Grid item xs={12}>
                          <Card variant="outlined" sx={{ borderRadius: 2, boxShadow: 1, p: 2, display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: 80, cursor: 'pointer', transition: 'box-shadow 0.2s', '&:hover': { boxShadow: 4, bgcolor: '#e3f2fd' } }}>
                            <input
                              id={`file-upload-${profile.id}`}
                              type="file"
                              name="file"
                              accept=".json,.vsix,.zip"
                              style={{ display: 'none' }}
                              onChange={e => {
                                if (e.target.files?.[0]) {
                                  handleFileUpload(profile.id, e.target.files[0]);
                                  e.target.value = '';
                                }
                              }}
                            />
                            <label htmlFor={`file-upload-${profile.id}`} style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}>
                              <AddIcon color="primary" sx={{ fontSize: 40 }} />
                            </label>
                          </Card>
                        </Grid>
                      </Grid>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
            {/* Add new profile card */}
            <Grid item xs={12} md={6} lg={4} key="add-profile">
              <Card
                sx={{
                  borderRadius: 3,
                  boxShadow: 3,
                  minHeight: 320,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  cursor: 'pointer',
                  transition: 'box-shadow 0.2s',
                  '&:hover': { boxShadow: 6, bgcolor: '#e3f2fd' },
                }}
                onClick={() => setCreateDialogOpen(true)}
              >
                <Box display="flex" flexDirection="column" alignItems="center" justifyContent="center">
                  <AddCircleOutlineIcon color="primary" sx={{ fontSize: 64 }} />
                  <Typography color="primary" fontWeight={600} mt={2}>Add New Profile</Typography>
                </Box>
              </Card>
            </Grid>
          </>
        )}
      </Grid>
    </Box>
  );
}
