<script lang="ts">
	import { onMount } from 'svelte';
	import { api, type Device } from '$lib/api/client';

	let devices: Device[] = [];
	let loading = true;
	let error = '';

	onMount(async () => {
		try {
			devices = await api.getDevices();
			loading = false;
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to fetch devices';
			loading = false;
		}
	});
</script>

<div class="container">
	<h1>PiSniffer - API Connection Test</h1>

	{#if loading}
		<p>Loading devices...</p>
	{:else if error}
		<div class="error">
			<p>❌ Error: {error}</p>
			<p>Make sure the API is running at http://192.168.0.4:8000</p>
		</div>
	{:else}
		<div class="success">
			<p>✅ API Connection Successful!</p>
			<p>Found {devices.length} devices</p>
		</div>

		<h2>Devices</h2>
		<table>
			<thead>
				<tr>
					<th>MAC</th>
					<th>Name</th>
					<th>Trusted</th>
					<th>Last Seen</th>
				</tr>
			</thead>
			<tbody>
				{#each devices.slice(0, 10) as device}
					<tr>
						<td>{device.mac}</td>
						<td>{device.name || '(unnamed)'}</td>
						<td>{device.is_trusted ? '✓' : '✗'}</td>
						<td>{device.last_seen}</td>
					</tr>
				{/each}
			</tbody>
		</table>
		{#if devices.length > 10}
			<p>Showing first 10 of {devices.length} devices</p>
		{/if}
	{/if}
</div>

<style>
	.container {
		max-width: 1200px;
		margin: 0 auto;
		padding: 2rem;
	}

	h1 {
		color: #333;
	}

	.error {
		background: #fee;
		border: 1px solid #fcc;
		padding: 1rem;
		border-radius: 4px;
		color: #c00;
	}

	.success {
		background: #efe;
		border: 1px solid #cfc;
		padding: 1rem;
		border-radius: 4px;
		color: #060;
	}

	table {
		width: 100%;
		border-collapse: collapse;
		margin-top: 1rem;
	}

	th,
	td {
		text-align: left;
		padding: 0.5rem;
		border-bottom: 1px solid #ddd;
	}

	th {
		background: #f5f5f5;
		font-weight: 600;
	}

	tr:hover {
		background: #fafafa;
	}
</style>
