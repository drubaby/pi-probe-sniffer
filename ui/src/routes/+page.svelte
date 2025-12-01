<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api/client';

	let deviceCount = 0;
	let trustedCount = 0;
	let loading = true;

	onMount(async () => {
		try {
			const devices = await api.getDevices();
			deviceCount = devices.length;
			trustedCount = devices.filter((d) => d.is_trusted).length;
		} catch (e) {
			console.error('Failed to load stats:', e);
		} finally {
			loading = false;
		}
	});
</script>

<div class="container">
	<header>
		<h1>PiSniffer</h1>
		<p class="tagline">WiFi Probe Request Monitor</p>
	</header>

	{#if !loading}
		<div class="stats">
			<div class="stat-card">
				<div class="stat-value">{deviceCount}</div>
				<div class="stat-label">Total Devices</div>
			</div>
			<div class="stat-card">
				<div class="stat-value">{trustedCount}</div>
				<div class="stat-label">Trusted</div>
			</div>
			<div class="stat-card">
				<div class="stat-value">{deviceCount - trustedCount}</div>
				<div class="stat-label">Unknown</div>
			</div>
		</div>
	{/if}

	<nav class="nav-cards">
		<a href="/devices" class="nav-card">
			<h2>📱 Devices</h2>
			<p>Manage and identify WiFi probe devices</p>
		</a>

		<div class="nav-card disabled">
			<h2>📊 Live Feed</h2>
			<p>Real-time probe stream (coming soon)</p>
		</div>

		<div class="nav-card disabled">
			<h2>📈 Dashboard</h2>
			<p>Statistics and insights (coming soon)</p>
		</div>
	</nav>
</div>

<style>
	.container {
		max-width: 1200px;
		margin: 0 auto;
		padding: 2rem;
	}

	header {
		text-align: center;
		margin-bottom: 3rem;
	}

	h1 {
		margin: 0;
		font-size: 3rem;
		color: #1a1a1a;
	}

	.tagline {
		margin: 0.5rem 0 0;
		color: #666;
		font-size: 1.2rem;
	}

	.stats {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
		gap: 1rem;
		margin-bottom: 3rem;
	}

	.stat-card {
		background: white;
		padding: 2rem;
		border-radius: 8px;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
		text-align: center;
	}

	.stat-value {
		font-size: 3rem;
		font-weight: bold;
		color: #007bff;
	}

	.stat-label {
		margin-top: 0.5rem;
		color: #666;
		font-size: 0.9rem;
		text-transform: uppercase;
		letter-spacing: 1px;
	}

	.nav-cards {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
		gap: 1.5rem;
	}

	.nav-card {
		background: white;
		padding: 2rem;
		border-radius: 8px;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
		text-decoration: none;
		color: inherit;
		transition: all 0.2s;
		border: 2px solid transparent;
	}

	.nav-card:not(.disabled):hover {
		transform: translateY(-4px);
		box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
		border-color: #007bff;
	}

	.nav-card.disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.nav-card h2 {
		margin: 0 0 0.5rem;
		font-size: 1.5rem;
	}

	.nav-card p {
		margin: 0;
		color: #666;
	}
</style>
