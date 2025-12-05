<script lang="ts">
	import { onMount } from 'svelte';
	import { api, formatEasternTime, type DeviceIdentity } from '$lib/api/client';

	let identities: DeviceIdentity[] = [];
	let loading = true;
	let error = '';

	// Editing
	let editingIdentity: string | null = null;
	let editAlias = '';

	onMount(async () => {
		await loadIdentities();
	});

	async function loadIdentities() {
		try {
			loading = true;
			identities = await api.getIdentities();
			error = '';
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to fetch identities';
		} finally {
			loading = false;
		}
	}

	function startEdit(identity: DeviceIdentity) {
		editingIdentity = identity.identity_id;
		editAlias = identity.alias || '';
	}

	async function saveAlias(identityId: string) {
		try {
			await api.updateIdentityAlias(identityId, editAlias);
			editingIdentity = null;
			await loadIdentities();
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to save alias';
		}
	}

	function cancelEdit() {
		editingIdentity = null;
		editAlias = '';
	}
</script>

<div class="container">
	<header>
		<h1>Device Identities</h1>
		<p class="subtitle">Track devices across MAC randomization using IE fingerprinting</p>
	</header>

	{#if loading}
		<div class="loading">Loading identities...</div>
	{:else if error}
		<div class="error">
			<p>❌ {error}</p>
			<button on:click={loadIdentities}>Retry</button>
		</div>
	{:else if identities.length === 0}
		<div class="empty">
			<p>No device identities created yet</p>
			<p class="hint">Create identities from fingerprints to track specific devices</p>
		</div>
	{:else}
		<div class="results">
			<p class="count">
				{identities.length} {identities.length === 1 ? 'identity' : 'identities'}
			</p>
		</div>

		<table class="identity-table">
			<thead>
				<tr>
					<th>Alias</th>
					<th>Identity ID</th>
					<th>First Seen</th>
					<th>Last Seen</th>
					<th>Alias Set</th>
					<th>Actions</th>
				</tr>
			</thead>
			<tbody>
				{#each identities as identity (identity.identity_id)}
					<tr>
						<td class="alias">
							{#if editingIdentity === identity.identity_id}
								<input
									type="text"
									bind:value={editAlias}
									on:keydown={(e) => {
										if (e.key === 'Enter') saveAlias(identity.identity_id);
										if (e.key === 'Escape') cancelEdit();
									}}
									autofocus
								/>
							{:else}
								<button class="alias-btn" on:click={() => startEdit(identity)}>
									{#if identity.alias}
										<span class="alias-name">{identity.alias}</span>
									{:else}
										<span class="no-alias">(no alias)</span>
									{/if}
								</button>
							{/if}
						</td>
						<td class="identity-id">{identity.identity_id}</td>
						<td class="timestamp">{formatEasternTime(identity.first_seen)}</td>
						<td class="timestamp">{formatEasternTime(identity.last_seen)}</td>
						<td class="timestamp">
							{identity.alias_set_at ? formatEasternTime(identity.alias_set_at) : '—'}
						</td>
						<td class="actions">
							{#if editingIdentity === identity.identity_id}
								<button class="btn-save" on:click={() => saveAlias(identity.identity_id)}>
									Save
								</button>
								<button class="btn-cancel" on:click={cancelEdit}>Cancel</button>
							{:else}
								<a href="/identities/{identity.identity_id}" class="btn-view">View</a>
							{/if}
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
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

	.identity-table {
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

	.alias {
		font-weight: 600;
		font-size: 1rem;
	}

	.alias-name {
		color: #007bff;
	}

	.no-alias {
		color: #999;
		font-style: italic;
	}

	.alias-btn {
		background: none;
		border: none;
		padding: 0.25rem 0.5rem;
		cursor: pointer;
		text-decoration: underline;
		font-size: 1rem;
	}

	.alias-btn:hover .alias-name {
		color: #0056b3;
	}

	.alias input {
		padding: 0.25rem 0.5rem;
		border: 2px solid #007bff;
		border-radius: 4px;
		font-size: 0.9rem;
		width: 250px;
	}

	.identity-id {
		font-family: 'Monaco', 'Courier New', monospace;
		font-size: 0.85rem;
		color: #6c757d;
	}

	.timestamp {
		font-size: 0.85rem;
		color: #6c757d;
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
</style>
