/**
 * Svelte store for live probe feed
 */

import { writable } from 'svelte/store';
import type { Sighting } from '$lib/api/client';

// Live probe stream (last 100)
export const liveProbes = writable<Sighting[]>([]);

// Toggle to hide trusted devices in live feed
export const hideTrusted = writable<boolean>(true);

// WebSocket connection status
export const wsConnected = writable<boolean>(false);

/**
 * Add a new probe to the beginning of the list
 * Keeps only the last 100 probes
 */
export function addProbe(probe: Sighting) {
	liveProbes.update((probes) => {
		const updated = [probe, ...probes];
		return updated.slice(0, 100);
	});
}

/**
 * Clear all probes
 */
export function clearProbes() {
	liveProbes.set([]);
}
