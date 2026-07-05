package game

import (
	"image/color"
	"testing"

	tm "pacman/internal/tilemap"

	"github.com/hajimehoshi/ebiten/v2"
)

func TestGameDrawDoesNotPanic(t *testing.T) {
	// Disable audio in tests to avoid global context conflicts
	t.Setenv("PACMAN_DISABLE_AUDIO", "1")
	t.Setenv("PACMAN_CONFIG_DIR", t.TempDir())
	g := New()
	screen := ebiten.NewImage(g.ScreenWidth(), g.ScreenHeight())
	// Should not panic
	g.Draw(screen)
}

func TestNamePromptBackdropProvidesContrast(t *testing.T) {
	const (
		width  = 240
		height = 120
	)
	prompt := "Enter name: Player_"
	dst := ebiten.NewImage(width, height)
	dst.Fill(color.RGBA{R: 33, G: 33, B: 255, A: 255})

	drawNamePrompt(dst, prompt, width, height)
	textX, baselineY, panel := namePromptLayout(prompt, width, height)

	if panel.Min.X >= textX || panel.Max.X <= textX {
		t.Fatalf("panel must surround text horizontally: panel=%v textX=%d", panel, textX)
	}
	if panel.Min.Y >= baselineY || panel.Max.Y <= baselineY {
		t.Fatalf("panel must surround the text baseline: panel=%v baseline=%d", panel, baselineY)
	}
	if namePromptBackdropColor != (color.RGBA{A: 255}) {
		t.Fatalf("expected opaque black prompt backdrop, got %#v", namePromptBackdropColor)
	}
}

func TestLevelCompletePanelIsCenteredAndOpaque(t *testing.T) {
	const (
		width  = 448
		height = 496
	)
	panel := levelCompletePanelLayout(width, height)

	if panel.Dx() != levelCompletePanelWidth || panel.Dy() != levelCompletePanelHeight {
		t.Fatalf("panel size = %dx%d, want %dx%d", panel.Dx(), panel.Dy(), levelCompletePanelWidth, levelCompletePanelHeight)
	}
	if panel.Min.X+panel.Max.X != width || panel.Min.Y+panel.Max.Y != height {
		t.Fatalf("panel is not centered: panel=%v canvas=%dx%d", panel, width, height)
	}
	if levelCompleteBorderColor.A != 255 {
		t.Fatalf("level-complete border must be opaque, got %#v", levelCompleteBorderColor)
	}
}

func TestLayoutMatchesScreenSize(t *testing.T) {
	g := New()
	w, h := g.Layout(0, 0)
	if w != g.ScreenWidth() || h != g.ScreenHeight() {
		t.Fatalf("layout mismatch: got %dx%d want %dx%d", w, h, g.ScreenWidth(), g.ScreenHeight())
	}
}

func TestReverseDirMapping(t *testing.T) {
	if reverseDir(0) == 0 { // DirNone -> should return a valid dir (Left)
		t.Fatalf("reverseDir for none should not be none")
	}
}

func TestNearestOpenTileVariants(t *testing.T) {
	g := New()

	// Case 1: Already open tile returns itself
	openX, openY := -1, -1
	for y := 0; y < g.tileMap.Height && openX < 0; y++ {
		for x := 0; x < g.tileMap.Width && openX < 0; x++ {
			if !g.tileMap.IsWall(x, y) {
				openX, openY = x, y
			}
		}
	}
	if openX < 0 {
		t.Skip("no open tile found")
	}
	nx, ny := g.nearestOpenTile(openX, openY)
	if nx != openX || ny != openY {
		t.Fatalf("expected same coords for open tile, got %d,%d vs %d,%d", nx, ny, openX, openY)
	}

	// Case 2: Wall tile returns a nearby open tile
	wallX, wallY := -1, -1
	for y := 0; y < g.tileMap.Height && wallX < 0; y++ {
		for x := 0; x < g.tileMap.Width && wallX < 0; x++ {
			if g.tileMap.IsWall(x, y) {
				wallX, wallY = x, y
			}
		}
	}
	if wallX < 0 {
		t.Skip("no wall tile found")
	}
	nx, ny = g.nearestOpenTile(wallX, wallY)
	if g.tileMap.IsWall(nx, ny) {
		t.Fatalf("expected non-wall from nearestOpenTile, got wall at %d,%d", nx, ny)
	}

	// Case 3: Fallback when all walls
	// Force all walls
	for y := 0; y < g.tileMap.Height; y++ {
		for x := 0; x < g.tileMap.Width; x++ {
			g.tileMap.Tiles[y][x] = tm.TileWall
		}
	}
	fx, fy := g.nearestOpenTile(5, 5)
	if fx != 5 || fy != 5 {
		t.Fatalf("expected fallback to original when all walls, got %d,%d", fx, fy)
	}
}

func TestCanTurnToValidDirection(t *testing.T) {
	g := New()
	// Test that turning works in valid directions from starting position
	// Player starts at (14*16 + 8, 26*16 + 8) which is a horizontal corridor
	// Left and Right should be valid, Up should be blocked by wall
	if !g.canTurn(3) { // DirLeft - should be valid from starting position
		t.Fatalf("expected canTurn true for left direction from starting position")
	}
	if !g.canTurn(4) { // DirRight - should be valid from starting position
		t.Fatalf("expected canTurn true for right direction from starting position")
	}
	if g.canTurn(1) { // DirUp - should be blocked by wall
		t.Fatalf("expected canTurn false for up direction from starting position (wall above)")
	}
}
