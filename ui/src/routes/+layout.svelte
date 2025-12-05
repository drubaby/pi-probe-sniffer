<script lang="ts">
	import favicon from '$lib/assets/favicon.svg';
	import { page } from '$app/stores';

	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

<div class="app">
	<nav class="navbar">
		<div class="nav-container">
			<h1 class="logo">PiSniffer</h1>
			<div class="nav-links">
				<a href="/" class:active={$page.url.pathname === '/'}>Home</a>
				<a href="/devices" class:active={$page.url.pathname.startsWith('/devices')}>Devices</a>
				<a href="/fingerprints" class:active={$page.url.pathname.startsWith('/fingerprints')}>
					Fingerprints
				</a>
				<a href="/identities" class:active={$page.url.pathname.startsWith('/identities')}>
					Identities
				</a>
			</div>
		</div>
	</nav>

	<main class="main-content">
		{@render children()}
	</main>
</div>

<style>
	:global(body) {
		margin: 0;
		padding: 0;
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell,
			'Open Sans', 'Helvetica Neue', sans-serif;
		background: #f5f5f5;
	}

	.app {
		min-height: 100vh;
		display: flex;
		flex-direction: column;
	}

	.navbar {
		background: #fff;
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
		position: sticky;
		top: 0;
		z-index: 100;
	}

	.nav-container {
		max-width: 1400px;
		margin: 0 auto;
		padding: 1rem 2rem;
		display: flex;
		align-items: center;
		justify-content: space-between;
	}

	.logo {
		margin: 0;
		font-size: 1.5rem;
		color: #007bff;
		font-weight: 700;
	}

	.nav-links {
		display: flex;
		gap: 1.5rem;
	}

	.nav-links a {
		color: #495057;
		text-decoration: none;
		font-weight: 500;
		padding: 0.5rem 1rem;
		border-radius: 4px;
		transition: all 0.2s;
	}

	.nav-links a:hover {
		background: #f8f9fa;
		color: #007bff;
	}

	.nav-links a.active {
		background: #007bff;
		color: white;
	}

	.main-content {
		flex: 1;
	}
</style>
