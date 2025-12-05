<script lang="ts">
	import { onMount } from 'svelte';
	import { api, formatEasternTime, type Fingerprint, type FingerprintsResponse } from '$lib/api/client';

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

	async function goToPage(page: number) {
		currentPage = Math.max(1, Math.min(page, totalPages));
		await loadFingerprints();
	}
</script>

<div class="container">
	<header>
		<h1>Device Fingerprints</h1>
		<p class="subtitle">IE fingerprints captured from WiFi probe requests</p>
	</header>

	{#if loading}
		<div class="loading">Loading fingerprints...</div>
	{:else if error}
		<div class="error">
			<p>❌ {error}</p>
			<button on:click={loadFingerprints}>Retry</button>
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

		<table class="fingerprint-table">
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
						<td class="fingerprint-id">
							<code>{fingerprint.fingerprint_id}</code>
						</td>
						<td class="identity">
							{#if fingerprint.identity_id}
								<a href="/identities/{fingerprint.identity_id}" class="identity-link">
									{fingerprint.identity_id}
								</a>
							{:else}
								<span class="no-identity">(unassigned)</span>
							{/if}
						</td>
						<td class="sightings">
							<span class="sightings-count">{fingerprint.sighting_count}</span>
						</td>
						<td class="timestamp">{formatEasternTime(fingerprint.first_seen)}</td>
						<td class="timestamp">{formatEasternTime(fingerprint.last_seen)}</td>
						<td class="actions">
							<a href="/fingerprints/{fingerprint.fingerprint_id}" class="btn-view">View</a>
						</td>
					</tr>
				{/each}
			</tbody>
		</table>

		<!-- Pagination -->
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

	.loading,
	.empty {
		text-align: center;
		padding: 3rem;
		color: #666;
	}

	.hint {
		margin-top: 0.5rem;
		font-size: 0.9rem;
		color: #999;
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

	.fingerprint-table {
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
		padding: 0.75rem 1rem;
		font-weight: 600;
		color: #495057;
		font-size: 0.85rem;
		text-transform: uppercase;
		letter-spacing: 0.5px;
	}

	td {
		padding: 1rem;
		border-top: 1px solid #dee2e6;
	}

	tr:hover {
		background: #f8f9fa;
	}

	.fingerprint-id code {
		font-family: 'Monaco', 'Courier New', monospace;
		font-size: 0.9rem;
		color: #495057;
		background: #f8f9fa;
		padding: 0.25rem 0.5rem;
		border-radius: 4px;
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

	.no-identity {
		color: #999;
		font-style: italic;
		font-size: 0.85rem;
	}

	.sightings {
		text-align: center;
	}

	.sightings-count {
		display: inline-block;
		padding: 0.25rem 0.75rem;
		background: #e7f3ff;
		color: #0056b3;
		border-radius: 12px;
		font-size: 0.9rem;
		font-weight: 600;
		min-width: 50px;
	}

	.timestamp {
		font-size: 0.85rem;
		color: #6c757d;
	}

	.actions {
		white-space: nowrap;
	}

	.btn-view {
		display: inline-block;
		padding: 0.5rem 1rem;
		background: #007bff;
		color: white;
		text-decoration: none;
		border-radius: 4px;
		font-size: 0.85rem;
		transition: all 0.2s;
	}

	.btn-view:hover {
		background: #0056b3;
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

	button {
		padding: 0.5rem 1rem;
		border: none;
		border-radius: 4px;
		cursor: pointer;
		font-size: 0.85rem;
		transition: all 0.2s;
	}
</style>
