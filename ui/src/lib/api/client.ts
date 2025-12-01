/**
 * API Client for PiSniffer Backend
 * Centralized HTTP client for all API calls
 */

const API_BASE = 'http://192.168.0.4:8000';

export interface Device {
	mac: string;
	name: string | null;
	first_seen: string;
	last_seen: string;
	is_trusted: boolean;
}

export interface DeviceWithStats extends Device {
	total_sightings: number;
	avg_signal_dbm: number | null;
}

export interface Sighting {
	id: number;
	timestamp: string;
	mac: string;
	rssi: string;
	dbm: number;
	ssid: string | null;
	oui: string | null;
}

export interface SightingsResponse {
	sightings: Sighting[];
	total: number;
	limit: number;
	offset: number;
}

export interface DeviceActivity {
	by_hour: number[]; // 24 values
	by_day_of_week: number[]; // 7 values
	by_date: Record<string, number>; // Last 30 days
}

export interface OverviewStats {
	total_devices: number;
	new_today: number;
	new_this_week: number;
	trusted_count: number;
	unknown_count: number;
	most_active_today: {
		mac: string;
		name: string | null;
		sightings: number;
	} | null;
	top_manufacturers: Array<{
		oui: string;
		count: number;
	}>;
	probes_by_hour: number[]; // Last 24h
}

export const api = {
	// Devices
	async getDevices(filters: { is_trusted?: boolean } = {}): Promise<Device[]> {
		const params = new URLSearchParams();
		if (filters.is_trusted !== undefined) {
			params.set('is_trusted', String(filters.is_trusted));
		}
		const queryString = params.toString();
		const url = queryString ? `${API_BASE}/devices/?${queryString}` : `${API_BASE}/devices/`;
		const res = await fetch(url);
		if (!res.ok) throw new Error('Failed to fetch devices');
		return res.json();
	},

	async getDevice(mac: string): Promise<DeviceWithStats> {
		const res = await fetch(`${API_BASE}/devices/${mac}`);
		if (!res.ok) throw new Error('Failed to fetch device');
		return res.json();
	},

	async updateDevice(
		mac: string,
		data: { name?: string | null; is_trusted?: boolean }
	): Promise<Device> {
		const res = await fetch(`${API_BASE}/devices/${mac}`, {
			method: 'PUT',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify(data)
		});
		if (!res.ok) throw new Error('Failed to update device');
		return res.json();
	},

	// Activity (NEW - not implemented yet)
	async getDeviceActivity(mac: string): Promise<DeviceActivity> {
		const res = await fetch(`${API_BASE}/devices/${mac}/activity`);
		if (!res.ok) throw new Error('Failed to fetch device activity');
		return res.json();
	},

	// Sightings
	async getSightings(params: {
		mac?: string;
		limit?: number;
		offset?: number;
		order?: 'ASC' | 'DESC';
	}): Promise<SightingsResponse> {
		const searchParams = new URLSearchParams();
		if (params.mac) searchParams.set('mac', params.mac);
		if (params.limit) searchParams.set('limit', String(params.limit));
		if (params.offset) searchParams.set('offset', String(params.offset));
		if (params.order) searchParams.set('order', params.order);

		const res = await fetch(`${API_BASE}/sightings?${searchParams}`);
		if (!res.ok) throw new Error('Failed to fetch sightings');
		return res.json();
	},

	async getRecentSightings(limit = 50): Promise<Sighting[]> {
		const res = await fetch(`${API_BASE}/sightings/recent?limit=${limit}`);
		if (!res.ok) throw new Error('Failed to fetch recent sightings');
		return res.json();
	},

	// Stats (NEW - not implemented yet)
	async getOverviewStats(): Promise<OverviewStats> {
		const res = await fetch(`${API_BASE}/stats/overview`);
		if (!res.ok) throw new Error('Failed to fetch overview stats');
		return res.json();
	}
};
