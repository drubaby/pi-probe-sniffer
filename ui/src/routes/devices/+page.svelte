<script lang="ts">
	import { onMount } from 'svelte';
	import { api, type Device } from '$lib/api/client';

	let devices: Device[] = [];
	let loading = true;
	let error = '';

	// Filters
	let filterMode: 'all' | 'trusted' | 'untrusted' = 'untrusted';
	let searchQuery = '';
	let ouiFilter = '';
	let ssidFilter = '';

	// Pagination
	let currentPage = 1;
	const itemsPerPage = 50;

	// Sorting
	type SortColumn = 'mac' | 'oui' | 'name' | 'last_seen' | 'is_trusted';
	let sortColumn: SortColumn = 'last_seen';
	let sortDirection: 'asc' | 'desc' = 'desc';

	// Editing
	let editingDevice: string | null = null;
	let editName = '';

	onMount(async () => {
		await loadDevices();
	});

	async function loadDevices() {
		try {
			loading = true;
			devices = await api.getDevices();
			error = '';
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to fetch devices';
		} finally {
			loading = false;
		}
	}

	async function toggleTrust(device: Device) {
		try {
			await api.updateDevice(device.mac, { is_trusted: !device.is_trusted });
			await loadDevices();
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to update device';
		}
	}

	function startEdit(device: Device) {
		editingDevice = device.mac;
		editName = device.name || '';
	}

	async function saveName(mac: string) {
		try {
			await api.updateDevice(mac, { name: editName || null });
			editingDevice = null;
			await loadDevices();
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to save name';
		}
	}

	function cancelEdit() {
		editingDevice = null;
		editName = '';
	}

	function toggleSort(column: SortColumn) {
		if (sortColumn === column) {
			sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
		} else {
			sortColumn = column;
			sortDirection = 'asc';
		}
	}

	// Get unique OUIs and SSIDs for filter dropdowns
	$: uniqueOuis = Array.from(new Set(devices.map((d) => d.oui).filter((oui) => oui)))
		.sort();
	$: uniqueSsids = Array.from(
		new Set(devices.flatMap((d) => d.ssids || []).filter((ssid) => ssid))
	).sort();

	// Computed filtered devices
	$: filteredDevices = devices
		.filter((d) => {
			// Filter by trust status
			if (filterMode === 'trusted' && !d.is_trusted) return false;
			if (filterMode === 'untrusted' && d.is_trusted) return false;

			// Filter by OUI
			if (ouiFilter && d.oui !== ouiFilter) return false;

			// Filter by SSID
			if (ssidFilter && (!d.ssids || !d.ssids.includes(ssidFilter))) return false;

			// Filter by search query
			if (searchQuery) {
				const query = searchQuery.toLowerCase();
				return (
					d.mac.toLowerCase().includes(query) ||
					(d.name && d.name.toLowerCase().includes(query))
				);
			}

			return true;
		})
		.sort((a, b) => {
			let comparison = 0;

			switch (sortColumn) {
				case 'mac':
					comparison = a.mac.localeCompare(b.mac);
					break;
				case 'oui':
					const ouiA = a.oui || '';
					const ouiB = b.oui || '';
					comparison = ouiA.localeCompare(ouiB);
					break;
				case 'name':
					const nameA = a.name || '';
					const nameB = b.name || '';
					comparison = nameA.localeCompare(nameB);
					break;
				case 'last_seen':
					comparison = a.last_seen.localeCompare(b.last_seen);
					break;
				case 'is_trusted':
					comparison = Number(a.is_trusted) - Number(b.is_trusted);
					break;
			}

			return sortDirection === 'asc' ? comparison : -comparison;
		});

	// Pagination calculations
	$: totalPages = Math.ceil(filteredDevices.length / itemsPerPage);
	$: paginatedDevices = filteredDevices.slice(
		(currentPage - 1) * itemsPerPage,
		currentPage * itemsPerPage
	);

	// Reset to page 1 when filters change
	$: if (filterMode || searchQuery || ouiFilter || ssidFilter) {
		currentPage = 1;
	}

	function goToPage(page: number) {
		currentPage = Math.max(1, Math.min(page, totalPages));
	}
</script>

<div class="container">
	<header>
		<h1>Device Management</h1>
		<p class="subtitle">Manage and identify WiFi probe devices</p>
	</header>

	<!-- Filters & Search -->
	<div class="controls">
		<div class="filters">
			<button
				class="filter-btn"
				class:active={filterMode === 'all'}
				on:click={() => (filterMode = 'all')}
			>
				All ({devices.length})
			</button>
			<button
				class="filter-btn"
				class:active={filterMode === 'untrusted'}
				on:click={() => (filterMode = 'untrusted')}
			>
				Unknown ({devices.filter((d) => !d.is_trusted).length})
			</button>
			<button
				class="filter-btn"
				class:active={filterMode === 'trusted'}
				on:click={() => (filterMode = 'trusted')}
			>
				Trusted ({devices.filter((d) => d.is_trusted).length})
			</button>
		</div>

		<div class="search">
			<input type="text" bind:value={searchQuery} placeholder="Search by MAC or name..." />
		</div>
	</div>

	<!-- Column Filters -->
	<div class="column-filters">
		<div class="filter-group">
			<label for="oui-filter">Manufacturer:</label>
			<select id="oui-filter" bind:value={ouiFilter}>
				<option value="">All Manufacturers</option>
				{#each uniqueOuis as oui}
					<option value={oui}>{oui}</option>
				{/each}
			</select>
		</div>

		<div class="filter-group">
			<label for="ssid-filter">SSID:</label>
			<select id="ssid-filter" bind:value={ssidFilter}>
				<option value="">All SSIDs</option>
				{#each uniqueSsids as ssid}
					<option value={ssid}>{ssid}</option>
				{/each}
			</select>
		</div>

		{#if ouiFilter || ssidFilter}
			<button
				class="clear-filters-btn"
				on:click={() => {
					ouiFilter = '';
					ssidFilter = '';
				}}
			>
				Clear Filters
			</button>
		{/if}
	</div>

	{#if loading}
		<div class="loading">Loading devices...</div>
	{:else if error}
		<div class="error">
			<p>❌ {error}</p>
			<button on:click={loadDevices}>Retry</button>
		</div>
	{:else if filteredDevices.length === 0}
		<div class="empty">
			<p>No devices found</p>
			{#if searchQuery}
				<button on:click={() => (searchQuery = '')}>Clear search</button>
			{/if}
		</div>
	{:else}
		<div class="results">
			<p class="count">
				Showing {(currentPage - 1) * itemsPerPage + 1}-{Math.min(
					currentPage * itemsPerPage,
					filteredDevices.length
				)} of {filteredDevices.length} devices
			</p>
		</div>

		<table class="device-table">
			<thead>
				<tr>
					<th>
						<button class="sort-header" on:click={() => toggleSort('mac')}>
							MAC Address
							{#if sortColumn === 'mac'}
								<span class="sort-icon">{sortDirection === 'asc' ? '↑' : '↓'}</span>
							{/if}
						</button>
					</th>
					<th>
						<button class="sort-header" on:click={() => toggleSort('oui')}>
							Manufacturer
							{#if sortColumn === 'oui'}
								<span class="sort-icon">{sortDirection === 'asc' ? '↑' : '↓'}</span>
							{/if}
						</button>
					</th>
					<th>
						<button class="sort-header" on:click={() => toggleSort('name')}>
							Name
							{#if sortColumn === 'name'}
								<span class="sort-icon">{sortDirection === 'asc' ? '↑' : '↓'}</span>
							{/if}
						</button>
					</th>
					<th>Probed SSIDs</th>
					<th>
						<button class="sort-header" on:click={() => toggleSort('last_seen')}>
							Last Seen
							{#if sortColumn === 'last_seen'}
								<span class="sort-icon">{sortDirection === 'asc' ? '↑' : '↓'}</span>
							{/if}
						</button>
					</th>
					<th>
						<button class="sort-header" on:click={() => toggleSort('is_trusted')}>
							Trusted
							{#if sortColumn === 'is_trusted'}
								<span class="sort-icon">{sortDirection === 'asc' ? '↑' : '↓'}</span>
							{/if}
						</button>
					</th>
					<th>Actions</th>
				</tr>
			</thead>
			<tbody>
				{#each paginatedDevices as device (device.mac)}
					<tr class:trusted={device.is_trusted}>
						<td class="mac">{device.mac}</td>
						<td class="oui">{device.oui || 'Unknown'}</td>
						<td class="name">
							{#if editingDevice === device.mac}
								<input
									type="text"
									bind:value={editName}
									on:keydown={(e) => {
										if (e.key === 'Enter') saveName(device.mac);
										if (e.key === 'Escape') cancelEdit();
									}}
									autofocus
								/>
							{:else}
								<button class="name-btn" on:click={() => startEdit(device)}>
									{device.name || '(unnamed)'}
								</button>
							{/if}
						</td>
						<td class="ssids">
							{#if device.ssids && device.ssids.length > 0}
								<span class="ssid-list">
									{#each device.ssids.slice(0, 3) as ssid}
										<span class="ssid-badge">{ssid}</span>
									{/each}
									{#if device.ssids.length > 3}
										<span class="ssid-more">+{device.ssids.length - 3} more</span>
									{/if}
								</span>
							{:else}
								<span class="no-ssids">(none)</span>
							{/if}
						</td>
						<td class="last-seen">{new Date(device.last_seen).toLocaleString()}</td>
						<td class="trust-status">
							{#if device.is_trusted}
								<span class="badge trusted">✓ Trusted</span>
							{:else}
								<span class="badge untrusted">✗ Unknown</span>
							{/if}
						</td>
						<td class="actions">
							{#if editingDevice === device.mac}
								<button class="btn-save" on:click={() => saveName(device.mac)}>Save</button>
								<button class="btn-cancel" on:click={cancelEdit}>Cancel</button>
							{:else}
								<button class="btn-toggle" on:click={() => toggleTrust(device)}>
									{device.is_trusted ? 'Untrust' : 'Trust'}
								</button>
							{/if}
						</td>
					</tr>
				{/each}
			</tbody>
		</table>

		<!-- Pagination Controls -->
		{#if totalPages > 1}
			<div class="pagination">
				<button
					class="page-btn"
					on:click={() => goToPage(currentPage - 1)}
					disabled={currentPage === 1}
				>
					← Previous
				</button>

				<div class="page-numbers">
					{#if currentPage > 2}
						<button class="page-btn" on:click={() => goToPage(1)}>1</button>
						{#if currentPage > 3}
							<span class="page-ellipsis">...</span>
						{/if}
					{/if}

					{#if currentPage > 1}
						<button class="page-btn" on:click={() => goToPage(currentPage - 1)}>
							{currentPage - 1}
						</button>
					{/if}

					<button class="page-btn active">{currentPage}</button>

					{#if currentPage < totalPages}
						<button class="page-btn" on:click={() => goToPage(currentPage + 1)}>
							{currentPage + 1}
						</button>
					{/if}

					{#if currentPage < totalPages - 1}
						{#if currentPage < totalPages - 2}
							<span class="page-ellipsis">...</span>
						{/if}
						<button class="page-btn" on:click={() => goToPage(totalPages)}>
							{totalPages}
						</button>
					{/if}
				</div>

				<button
					class="page-btn"
					on:click={() => goToPage(currentPage + 1)}
					disabled={currentPage === totalPages}
				>
					Next →
				</button>
			</div>
		{/if}
	{/if}
</div>

<style>
	.container {
		max-width: 1400px;
		margin: 0 auto;
		padding: 2rem;
	}

	header {
		margin-bottom: 2rem;
	}

	h1 {
		margin: 0;
		font-size: 2rem;
		color: #1a1a1a;
	}

	.subtitle {
		margin: 0.5rem 0 0;
		color: #666;
	}

	.controls {
		display: flex;
		gap: 1rem;
		margin-bottom: 1.5rem;
		flex-wrap: wrap;
	}

	.filters {
		display: flex;
		gap: 0.5rem;
	}

	.filter-btn {
		padding: 0.5rem 1rem;
		border: 2px solid #ddd;
		background: white;
		border-radius: 6px;
		cursor: pointer;
		font-size: 0.9rem;
		transition: all 0.2s;
	}

	.filter-btn:hover {
		border-color: #999;
	}

	.filter-btn.active {
		background: #007bff;
		color: white;
		border-color: #007bff;
	}

	.search {
		flex: 1;
		min-width: 250px;
	}

	.search input {
		width: 100%;
		padding: 0.5rem 1rem;
		border: 2px solid #ddd;
		border-radius: 6px;
		font-size: 0.9rem;
	}

	.search input:focus {
		outline: none;
		border-color: #007bff;
	}

	.column-filters {
		display: flex;
		gap: 1rem;
		align-items: center;
		margin-bottom: 1.5rem;
		flex-wrap: wrap;
	}

	.filter-group {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.filter-group label {
		font-size: 0.9rem;
		color: #495057;
		font-weight: 500;
	}

	.filter-group select {
		padding: 0.5rem 1rem;
		border: 2px solid #ddd;
		border-radius: 6px;
		font-size: 0.9rem;
		background: white;
		cursor: pointer;
		min-width: 200px;
	}

	.filter-group select:focus {
		outline: none;
		border-color: #007bff;
	}

	.clear-filters-btn {
		padding: 0.5rem 1rem;
		background: #dc3545;
		color: white;
		border: none;
		border-radius: 6px;
		cursor: pointer;
		font-size: 0.9rem;
		transition: background 0.2s;
	}

	.clear-filters-btn:hover {
		background: #c82333;
	}

	.loading,
	.empty {
		text-align: center;
		padding: 3rem;
		color: #666;
	}

	.error {
		background: #fee;
		border: 1px solid #fcc;
		padding: 1rem;
		border-radius: 6px;
		color: #c00;
		text-align: center;
	}

	.error button {
		margin-top: 0.5rem;
	}

	.results {
		margin-bottom: 1rem;
	}

	.count {
		color: #666;
		font-size: 0.9rem;
	}

	.device-table {
		width: 100%;
		border-collapse: collapse;
		background: white;
		box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
		border-radius: 6px;
		overflow: hidden;
	}

	thead {
		background: #f8f9fa;
	}

	th {
		text-align: left;
		padding: 0.5rem 1rem;
		font-weight: 600;
		color: #495057;
		font-size: 0.85rem;
		text-transform: uppercase;
		letter-spacing: 0.5px;
	}

	.sort-header {
		background: none;
		border: none;
		padding: 0.5rem 0;
		cursor: pointer;
		color: #495057;
		font-size: 0.85rem;
		text-transform: uppercase;
		letter-spacing: 0.5px;
		font-weight: 600;
		display: flex;
		align-items: center;
		gap: 0.5rem;
		width: 100%;
		transition: color 0.2s;
	}

	.sort-header:hover {
		color: #007bff;
	}

	.sort-icon {
		font-size: 1rem;
		color: #007bff;
	}

	td {
		padding: 1rem;
		border-top: 1px solid #dee2e6;
	}

	tr:hover {
		background: #f8f9fa;
	}

	tr.trusted {
		opacity: 0.6;
	}

	.mac {
		font-family: 'Monaco', 'Courier New', monospace;
		font-size: 0.9rem;
		color: #495057;
	}

	.oui {
		font-size: 0.85rem;
		color: #6c757d;
		max-width: 200px;
	}

	.ssids {
		max-width: 300px;
	}

	.ssid-list {
		display: flex;
		flex-wrap: wrap;
		gap: 0.25rem;
	}

	.ssid-badge {
		display: inline-block;
		padding: 0.2rem 0.5rem;
		background: #e7f3ff;
		color: #0056b3;
		border-radius: 4px;
		font-size: 0.75rem;
		font-family: 'Monaco', 'Courier New', monospace;
	}

	.ssid-more {
		font-size: 0.75rem;
		color: #6c757d;
		font-style: italic;
	}

	.no-ssids {
		font-size: 0.85rem;
		color: #999;
		font-style: italic;
	}

	.name-btn {
		background: none;
		border: none;
		padding: 0.25rem 0.5rem;
		cursor: pointer;
		color: #007bff;
		text-decoration: underline;
		font-size: 0.9rem;
	}

	.name-btn:hover {
		color: #0056b3;
	}

	.name input {
		padding: 0.25rem 0.5rem;
		border: 2px solid #007bff;
		border-radius: 4px;
		font-size: 0.9rem;
		width: 200px;
	}

	.last-seen {
		font-size: 0.85rem;
		color: #6c757d;
	}

	.badge {
		display: inline-block;
		padding: 0.25rem 0.75rem;
		border-radius: 12px;
		font-size: 0.8rem;
		font-weight: 600;
	}

	.badge.trusted {
		background: #d4edda;
		color: #155724;
	}

	.badge.untrusted {
		background: #fff3cd;
		color: #856404;
	}

	.actions {
		white-space: nowrap;
	}

	button {
		padding: 0.5rem 1rem;
		border: none;
		border-radius: 4px;
		cursor: pointer;
		font-size: 0.85rem;
		transition: all 0.2s;
	}

	.btn-toggle {
		background: #007bff;
		color: white;
	}

	.btn-toggle:hover {
		background: #0056b3;
	}

	.btn-save {
		background: #28a745;
		color: white;
		margin-right: 0.5rem;
	}

	.btn-save:hover {
		background: #218838;
	}

	.btn-cancel {
		background: #6c757d;
		color: white;
	}

	.btn-cancel:hover {
		background: #5a6268;
	}

	/* Pagination */
	.pagination {
		display: flex;
		justify-content: center;
		align-items: center;
		gap: 0.5rem;
		margin-top: 2rem;
		padding: 1rem;
	}

	.page-numbers {
		display: flex;
		gap: 0.25rem;
		align-items: center;
	}

	.page-btn {
		min-width: 40px;
		padding: 0.5rem 1rem;
		border: 1px solid #dee2e6;
		background: white;
		border-radius: 4px;
		cursor: pointer;
		font-size: 0.9rem;
		transition: all 0.2s;
	}

	.page-btn:hover:not(:disabled):not(.active) {
		background: #f8f9fa;
		border-color: #007bff;
	}

	.page-btn.active {
		background: #007bff;
		color: white;
		border-color: #007bff;
		font-weight: 600;
	}

	.page-btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.page-ellipsis {
		padding: 0 0.5rem;
		color: #6c757d;
	}
</style>
