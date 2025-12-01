/**
 * Svelte store for device state management
 */

import { writable } from 'svelte/store';
import type { Device, DeviceWithStats } from '$lib/api/client';

// All devices list
export const devices = writable<Device[]>([]);

// Currently selected/viewing device
export const selectedDevice = writable<DeviceWithStats | null>(null);

// Filter state
export const deviceFilter = writable<'all' | 'trusted' | 'untrusted'>('untrusted');

// Search query
export const searchQuery = writable<string>('');
