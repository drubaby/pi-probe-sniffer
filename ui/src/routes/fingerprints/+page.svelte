<script lang="ts">
	import { onMount } from 'svelte';
	import { api, formatEasternTime, type FingerprintsResponse } from '$lib/api/client';
	import PageHeader from '$lib/components/PageHeader.svelte';
	import Pagination from '$lib/components/Pagination.svelte';

	let response: FingerprintsResponse | null = null;
	let loading = true;
	let error = '';

	// Pagination
	let currentPage = 1;
	const itemsPerPage = 50;

	onMount(async () => {
		await loadFingerprints();
	});

	async function loadFingerprints() {
		try {
			loading = true;
			response = await api.getFingerprints({
				limit: itemsPerPage,
				offset: (currentPage - 1) * itemsPerPage
			});
			error = '';
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to fetch fingerprints';
		} finally {
			loading = false;
		}
	}

	$: totalPages = response ? Math.ceil(response.total / itemsPerPage) : 0;

	async function handlePageChange(page: number) {
		currentPage = page;
		await loadFingerprints();
	}
</script>

<div class="container">
	<PageHeader
		title="Device Fingerprints"
		subtitle="IE fingerprints captured from WiFi probe requests"
	/>

	{#if loading}
		<div class="loading">Loading fingerprints...</div>
	{:else if error}
		<div class="error">
			<p>❌ {error}</p>
			<button onclick={loadFingerprints}>Retry</button>
		</div>
	{:else if !response || response.fingerprints.length === 0}
		<div class="empty">
			<p>No fingerprints captured yet</p>
			<p class="hint">Fingerprints will appear as devices send probe requests</p>
		</div>
	{:else}
		<div class="results">
			<p class="count">
				Showing {(currentPage - 1) * itemsPerPage + 1}-{Math.min(
					currentPage * itemsPerPage,
					response.total
				)} of {response.total} fingerprints
			</p>
		</div>

		<table class="data-table">
			<thead>
				<tr>
					<th>Fingerprint ID</th>
					<th>Identity</th>
					<th>Sightings</th>
					<th>First Seen</th>
					<th>Last Seen</th>
					<th>Actions</th>
				</tr>
			</thead>
			<tbody>
				{#each response.fingerprints as fingerprint (fingerprint.fingerprint_id)}
					<tr>
						<td>
							<code>{fingerprint.fingerprint_id}</code>
						</td>
						<td>
							{#if fingerprint.identity_id}
								<a href="/identities/{fingerprint.identity_id}" class="identity-link">
									{fingerprint.identity_id}
								</a>
							{:else}
								<span class="no-value">(unassigned)</span>
							{/if}
						</td>
						<td class="sightings-col">
							<span class="badge">{fingerprint.sighting_count}</span>
						</td>
						<td class="timestamp">{formatEasternTime(fingerprint.first_seen)}</td>
						<td class="timestamp">{formatEasternTime(fingerprint.last_seen)}</td>
						<td>
							<a href="/fingerprints/{fingerprint.fingerprint_id}" class="btn-view">View</a>
						</td>
					</tr>
				{/each}
			</tbody>
		</table>

		<Pagination {currentPage} {totalPages} onPageChange={handlePageChange} />
	{/if}
</div>

<style>
	.container {
		max-width: 1400px;
		margin: 0 auto;
		padding: 2rem;
	}

	.identity-link {
		color: #007bff;
		text-decoration: none;
		font-family: 'Monaco', 'Courier New', monospace;
		font-size: 0.85rem;
	}

	.identity-link:hover {
		text-decoration: underline;
	}

	.sightings-col {
		text-align: center;
	}
</style>
