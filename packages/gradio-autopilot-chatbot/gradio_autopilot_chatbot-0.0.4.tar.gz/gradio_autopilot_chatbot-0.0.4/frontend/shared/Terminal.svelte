<script lang="ts">
  import { onMount, afterUpdate } from "svelte";

  /** Array of text lines to display */
  export let lines: string[] = [];

  let scroller: HTMLDivElement;
  const scrollToBottom = () =>
    scroller && (scroller.scrollTop = scroller.scrollHeight);

  onMount(scrollToBottom);
  afterUpdate(scrollToBottom);
</script>

<div class="terminal max-height-320px full-width">
  <div class="titlebar">
    <div class="lights height-32px">
      <button class="light close" aria-label="Close"></button>
      <button class="light minimize" aria-label="Minimize"></button>
      <button class="light zoom" aria-label="Zoom"></button>
    </div>
  </div>

  <div class="screen" bind:this={scroller}>
    {#each lines as line, i (i)}
      <div class="row">{line}</div>
    {/each}
  </div>
</div>

<style>
  :global(:root) {
    --term-bg: #111315;
    --term-fg: #e7e7e7;
    --titlebar-start: #e8e8e8;
    --titlebar-end: #cfcfcf;
    --titlebar-border: #bdbdbd;
    --window-border: #1f2327;
  }

  .terminal {
    display: flex;
    flex-direction: column;
    width: 100%;
    background: var(--term-bg);
    color: var(--term-fg);
    border: 1px solid var(--window-border);
    border-radius: 12px;
    overflow: hidden;
    box-shadow:
      0 8px 30px rgba(0, 0, 0, 0.35),
      inset 0 1px 0 rgba(255, 255, 255, 0.02);
  }

  .titlebar {
    display: flex;
    align-items: center;
    height: 32px;
    padding: 0 12px;
    background: linear-gradient(var(--titlebar-start), var(--titlebar-end));
    border-bottom: 1px solid var(--titlebar-border);
    user-select: none;
  }

  .lights {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .light {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    border: 1px solid rgba(0, 0, 0, 0.15);
    box-shadow:
      inset 0 0 0 1px rgba(255, 255, 255, 0.35),
      0 1px 1px rgba(0, 0, 0, 0.08);
    background: #ccc;
    appearance: none;
    outline: none;
  }

  .light.close {
    background: #ff5f57;
    border-color: #e0443e;
  }
  .light.minimize {
    background: #febc2e;
    border-color: #d49d27;
  }
  .light.zoom {
    background: #28c840;
    border-color: #23a137;
  }

  .screen {
    flex: 1;
    overflow: auto;
    padding: 14px 16px;
    background: radial-gradient(
        200% 60% at 50% -40%,
        rgba(255, 255, 255, 0.04),
        transparent 60%
      ),
      var(--term-bg);
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas,
      "Liberation Mono", monospace;
    font-size: 13px;
    line-height: 1.6;
    scrollbar-gutter: stable both-edges;
  }

  .row {
    white-space: pre-wrap;
    word-break: break-word;
  }

  .max-height-320px {
    max-height: 320px;
  }

  .full-width {
    width: 100%;
  }

  .height-32px {
    height: 32px;
  }
</style>
