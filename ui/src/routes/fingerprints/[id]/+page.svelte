<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { api, formatEasternTime, type FingerprintWithDetails } from '$lib/api/client';

	let fingerprint: FingerprintWithDetails | null = null;
	let loading = true;
	let error = '';

	$: fingerprintId = $page.params.id;

	onMount(async () => {
		await loadFingerprint();
	});

	async function loadFingerprint() {
		try {
			loading = true;
			fingerprint = await api.getFingerprint(fingerprintId);
			error = '';
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to fetch fingerprint';
		} finally {
			loading = false;
		}
	}

	function parseIEData(ieDataJson: string | null): any[] | null {
		if (!ieDataJson) return null;
		try {
			return JSON.parse(ieDataJson);
		} catch {
			return null;
		}
	}

	$: ieData = fingerprint ? parseIEData(fingerprint.ie_data) : null;
</script>

<div class="container">
	<div class="breadcrumb">
		<a href="/fingerprints">← Back to Fingerprints</a>
	</div>

	{#if loading}
		<div class="loading">Loading fingerprint...</div>
	{:else if error}
		<div class="error">
			<p>❌ {error}</p>
			<button on:click={loadFingerprint}>Retry</button>
		</div>
	{:else if fingerprint}
		<header>
			<h1>Fingerprint Details</h1>
			<code class="fingerprint-id">{fingerprint.fingerprint_id}</code>
		</header>

		<div class="details-grid">
			<div class="card">
				<h2>Overview</h2>
				<dl>
					<dt>Fingerprint ID</dt>
					<dd><code>{fingerprint.fingerprint_id}</code></dd>

					<dt>Linked Identity</dt>
					<dd>
						{#if fingerprint.identity_id}
							<a href="/identities/{fingerprint.identity_id}" class="identity-link">
								{fingerprint.identity_id}
							</a>
						{:else}
							<span class="no-value">(unassigned)</span>
						{/if}
					</dd>

					<dt>Total Sightings</dt>
					<dd><span class="badge">{fingerprint.sighting_count}</span></dd>

					<dt>Unique MAC Addresses</dt>
					<dd><span class="badge">{fingerprint.unique_mac_count}</span></dd>

					<dt>First Seen</dt>
					<dd>{formatEasternTime(fingerprint.first_seen)}</dd>

					<dt>Last Seen</dt>
					<dd>{formatEasternTime(fingerprint.last_seen)}</dd>
				</dl>
			</div>

			<div class="card">
				<h2>SSID Signature</h2>
				{#if fingerprint.ssid_signature && fingerprint.ssid_signature.length > 0}
					<div class="ssid-list">
						{#each fingerprint.ssid_signature as ssid}
							<span class="ssid-badge">{ssid}</span>
						{/each}
					</div>
				{:else}
					<p class="no-value">No SSIDs captured</p>
				{/if}
			</div>
		</div>

		{#if ieData && ieData.length > 0}
			<div class="card ie-section">
				<h2>Information Elements ({ieData.length})</h2>
				<p class="hint">
					Raw IE data used to generate this fingerprint. IEs 0, 3, and 221 are excluded from
					fingerprint calculation.
				</p>
				<table class="ie-table">
					<thead>
						<tr>
							<th>IE ID</th>
							<th>Length</th>
							<th>Data (Hex)</th>
						</tr>
					</thead>
					<tbody>
						{#each ieData as ie}
							<tr>
								<td class="ie-id">{ie.id}</td>
								<td class="ie-len">{ie.len}</td>
								<td class="ie-data"><code>{ie.data}</code></td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		{/if}
	{/if}
</div>

<style>
	.container {
		max-width: 1200px;
		margin: 0 auto;
		padding: 2rem;
	}

	.breadcrumb {
		margin-bottom: 1.5rem;
	}

	.breadcrumb a {
		color: #007bff;
		text-decoration: none;
		font-size: 0.9rem;
	}

	.breadcrumb a:hover {
		text-decoration: underline;
	}

	header {
		margin-bottom: 2rem;
	}

	h1 {
		margin: 0 0 0.5rem;
		font-size: 2rem;
		color: #1a1a1a;
	}

	.fingerprint-id {
		font-family: 'Monaco', 'Courier New', monospace;
		font-size: 1.1rem;
		color: #6c757d;
		background: #f8f9fa;
		padding: 0.5rem 1rem;
		border-radius: 4px;
		display: inline-block;
	}

	.loading {
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

	.details-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
		gap: 1.5rem;
		margin-bottom: 1.5rem;
	}

	.card {
		background: white;
		border-radius: 8px;
		padding: 1.5rem;
		box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
	}

	.card h2 {
		margin: 0 0 1rem;
		font-size: 1.2rem;
		color: #495057;
	}

	dl {
		margin: 0;
	}

	dt {
		font-weight: 600;
		color: #6c757d;
		font-size: 0.85rem;
		text-transform: uppercase;
		letter-spacing: 0.5px;
		margin-top: 1rem;
	}

	dt:first-child {
		margin-top: 0;
	}

	dd {
		margin: 0.25rem 0 0;
		color: #1a1a1a;
		font-size: 1rem;
	}

	dd code {
		font-family: 'Monaco', 'Courier New', monospace;
		background: #f8f9fa;
		padding: 0.25rem 0.5rem;
		border-radius: 4px;
		font-size: 0.9rem;
	}

	.identity-link {
		color: #007bff;
		text-decoration: none;
	}

	.identity-link:hover {
		text-decoration: underline;
	}

	.no-value {
		color: #999;
		font-style: italic;
	}

	.badge {
		display: inline-block;
		padding: 0.25rem 0.75rem;
		background: #e7f3ff;
		color: #0056b3;
		border-radius: 12px;
		font-weight: 600;
		font-size: 0.9rem;
	}

	.ssid-list {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
	}

	.ssid-badge {
		display: inline-block;
		padding: 0.5rem 1rem;
		background: #e7f3ff;
		color: #0056b3;
		border-radius: 6px;
		font-family: 'Monaco', 'Courier New', monospace;
		font-size: 0.9rem;
	}

	.ie-section {
		grid-column: 1 / -1;
	}

	.hint {
		color: #6c757d;
		font-size: 0.9rem;
		margin-bottom: 1rem;
	}

	.ie-table {
		width: 100%;
		border-collapse: collapse;
		background: white;
	}

	.ie-table thead {
		background: #f8f9fa;
	}

	.ie-table th {
		text-align: left;
		padding: 0.75rem 1rem;
		font-weight: 600;
		color: #495057;
		font-size: 0.85rem;
		text-transform: uppercase;
		letter-spacing: 0.5px;
		border-bottom: 2px solid #dee2e6;
	}

	.ie-table td {
		padding: 0.75rem 1rem;
		border-bottom: 1px solid #dee2e6;
	}

	.ie-id,
	.ie-len {
		font-family: 'Monaco', 'Courier New', monospace;
		color: #495057;
	}

	.ie-data code {
		font-family: 'Monaco', 'Courier New', monospace;
		font-size: 0.85rem;
		color: #495057;
		word-break: break-all;
	}

	button {
		padding: 0.5rem 1rem;
		border: none;
		border-radius: 4px;
		cursor: pointer;
		background: #007bff;
		color: white;
		margin-top: 0.5rem;
	}

	button:hover {
		background: #0056b3;
	}
</style>
