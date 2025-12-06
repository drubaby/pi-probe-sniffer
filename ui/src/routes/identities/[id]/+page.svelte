<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { api, formatEasternTime, type DeviceIdentity } from '$lib/api/client';

	let identity: DeviceIdentity | null = null;
	let loading = true;
	let error = '';

	// Editing
	let editingAlias = false;
	let editAlias = '';

	$: identityId = page.params.id;

	onMount(async () => {
		await loadIdentity();
	});

	async function loadIdentity() {
		try {
			loading = true;
			identity = await api.getIdentity(identityId);
			error = '';
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to fetch identity';
		} finally {
			loading = false;
		}
	}

	function startEditAlias() {
		if (identity) {
			editingAlias = true;
			editAlias = identity.alias || '';
		}
	}

	async function saveAlias() {
		if (!identity) return;

		try {
			await api.updateIdentityAlias(identity.identity_id, editAlias);
			editingAlias = false;
			await loadIdentity();
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to save alias';
		}
	}

	function cancelEdit() {
		editingAlias = false;
		editAlias = '';
	}
</script>

<div class="container">
	<div class="breadcrumb">
		<a href="/identities">← Back to Identities</a>
	</div>

	{#if loading}
		<div class="loading">Loading identity...</div>
	{:else if error}
		<div class="error">
			<p>❌ {error}</p>
			<button onclick={loadIdentity}>Retry</button>
		</div>
	{:else if identity}
		<header>
			<div class="header-content">
				<div class="title-section">
					<h1>
						{#if editingAlias}
							<input
								type="text"
								bind:value={editAlias}
								on:keydown={(e) => {
									if (e.key === 'Enter') saveAlias();
									if (e.key === 'Escape') cancelEdit();
								}}
								class="alias-input"
								autofocus
							/>
						{:else if identity.alias}
							{identity.alias}
						{:else}
							<span class="no-alias">(No alias set)</span>
						{/if}
					</h1>
					<p class="identity-id">{identity.identity_id}</p>
				</div>
				<div class="header-actions">
					{#if editingAlias}
						<button class="btn-save" onclick={saveAlias}>Save</button>
						<button class="btn-cancel" onclick={cancelEdit}>Cancel</button>
					{:else}
						<button class="btn-edit" onclick={startEditAlias}>Edit Alias</button>
					{/if}
				</div>
			</div>
		</header>

		<div class="details-grid">
			<div class="card">
				<h2>Identity Information</h2>
				<dl>
					<dt>Identity ID</dt>
					<dd><code>{identity.identity_id}</code></dd>

					<dt>Alias</dt>
					<dd>
						{#if identity.alias}
							{identity.alias}
						{:else}
							<span class="no-value">(not set)</span>
						{/if}
					</dd>

					<dt>Alias Set At</dt>
					<dd>
						{#if identity.alias_set_at}
							{formatEasternTime(identity.alias_set_at)}
						{:else}
							<span class="no-value">—</span>
						{/if}
					</dd>

					<dt>First Seen</dt>
					<dd>{formatEasternTime(identity.first_seen)}</dd>

					<dt>Last Seen</dt>
					<dd>{formatEasternTime(identity.last_seen)}</dd>

					<dt>Total Sightings</dt>
					<dd><span class="badge">{identity.total_sightings}</span></dd>
				</dl>
			</div>

			<div class="card">
				<h2>SSID Signature</h2>
				<p class="hint">Networks this device probes for</p>
				{#if identity.ssid_signature}
					{@const ssids = JSON.parse(identity.ssid_signature)}
					{#if ssids.length > 0}
						<div class="ssid-list">
							{#each ssids as ssid}
								<span class="ssid-badge">{ssid}</span>
							{/each}
						</div>
					{:else}
						<p class="no-value">No SSIDs recorded</p>
					{/if}
				{:else}
					<p class="no-value">No SSIDs recorded</p>
				{/if}
			</div>
		</div>

		<div class="card full-width">
			<h2>What is a Device Identity?</h2>
			<p class="info-text">
				A device identity represents a unique physical device tracked across MAC address randomization.
				It may be linked to multiple fingerprints as devices change their Information Elements over time
				(e.g., when switching power modes). The SSID signature helps validate that different fingerprints
				belong to the same device.
			</p>
		</div>
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
		background: white;
		border-radius: 8px;
		padding: 1.5rem;
		box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
	}

	.header-content {
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: 1rem;
		flex-wrap: wrap;
	}

	.title-section {
		flex: 1;
	}

	h1 {
		margin: 0 0 0.5rem;
		font-size: 2rem;
		color: #1a1a1a;
	}

	.no-alias {
		color: #999;
		font-style: italic;
	}

	.alias-input {
		font-size: 2rem;
		font-weight: 600;
		padding: 0.25rem 0.5rem;
		border: 2px solid #007bff;
		border-radius: 4px;
		width: 100%;
		max-width: 500px;
	}

	.identity-id {
		margin: 0;
		font-family: 'Monaco', 'Courier New', monospace;
		font-size: 0.9rem;
		color: #6c757d;
	}

	.header-actions {
		display: flex;
		gap: 0.5rem;
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

	.full-width {
		grid-column: 1 / -1;
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

	.hint {
		color: #6c757d;
		font-size: 0.85rem;
		margin-bottom: 1rem;
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

	.info-text {
		color: #6c757d;
		line-height: 1.6;
		margin: 0;
	}

	button {
		padding: 0.5rem 1rem;
		border: none;
		border-radius: 4px;
		cursor: pointer;
		font-size: 0.85rem;
		transition: all 0.2s;
	}

	.btn-edit {
		background: #007bff;
		color: white;
	}

	.btn-edit:hover {
		background: #0056b3;
	}

	.btn-save {
		background: #28a745;
		color: white;
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
</style>
