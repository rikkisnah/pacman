// #ai-assisted with OCA/OpenAI Model with human supervision

package game

import (
	"testing"

	"pacman/internal/entities"
	tm "pacman/internal/tilemap"

	"github.com/hajimehoshi/ebiten/v2"
)

func TestFinalPelletCompletesLevelEndToEnd(t *testing.T) {
	tests := []struct {
		name      string
		pellet    tm.Tile
		wantScore int
	}{
		{name: "regular pellet", pellet: tm.TilePellet, wantScore: pelletPoints},
		{name: "power pellet", pellet: tm.TilePower, wantScore: powerPelletPoints},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			g := newCompletionTestGame(t)
			placeOnlyPellets(g, tt.pellet)

			if err := g.Update(); err != nil {
				t.Fatalf("winning update returned an error: %v", err)
			}
			if !g.levelComplete {
				t.Fatal("expected final pellet to complete the level")
			}
			if got := g.tileMap.RemainingPellets(); got != 0 {
				t.Fatalf("remaining pellets = %d, want 0", got)
			}
			if g.score != tt.wantScore {
				t.Fatalf("score = %d, want %d", g.score, tt.wantScore)
			}

			record := LoadHighScoreRecord()
			if record == nil || record.Name != "Winner" || record.Score != tt.wantScore {
				t.Fatalf("persisted high score = %#v, want Winner/%d", record, tt.wantScore)
			}

			x, y, tick := g.player.X, g.player.Y, g.tickCounter
			g.player.CurrentDir = entities.DirRight
			g.player.DesiredDir = entities.DirRight
			if err := g.Update(); err != nil {
				t.Fatalf("completed-level update returned an error: %v", err)
			}
			if g.player.X != x || g.player.Y != y {
				t.Fatalf("player moved after completion: got (%v,%v), want (%v,%v)", g.player.X, g.player.Y, x, y)
			}
			if g.tickCounter != tick+1 {
				t.Fatalf("tick counter = %d, want %d", g.tickCounter, tick+1)
			}

			screen := ebiten.NewImage(g.ScreenWidth(), g.ScreenHeight())
			g.Draw(screen)
		})
	}
}

func TestNonFinalPelletDoesNotCompleteLevel(t *testing.T) {
	g := newCompletionTestGame(t)
	placeOnlyPellets(g, tm.TilePellet, tm.TilePellet)

	if err := g.Update(); err != nil {
		t.Fatalf("update returned an error: %v", err)
	}
	if g.levelComplete {
		t.Fatal("level completed while one pellet remained")
	}
	if got := g.tileMap.RemainingPellets(); got != 1 {
		t.Fatalf("remaining pellets = %d, want 1", got)
	}
}

func TestFinalPelletWinsBeforeGhostCollision(t *testing.T) {
	g := newCompletionTestGame(t)
	placeOnlyPellets(g, tm.TilePellet)
	g.ghosts = []*entities.Ghost{{
		X:     g.player.X,
		Y:     g.player.Y,
		State: entities.GhostNormal,
	}}
	wantLives := g.lives

	if err := g.Update(); err != nil {
		t.Fatalf("winning update returned an error: %v", err)
	}
	if !g.levelComplete {
		t.Fatal("expected final pellet to complete the level")
	}
	if g.lives != wantLives {
		t.Fatalf("lives = %d, want %d; ghost collision ran after winning", g.lives, wantLives)
	}
}

func TestFinalPelletPersistsWinnerBelowGlobalHighScore(t *testing.T) {
	t.Setenv("PACMAN_DISABLE_AUDIO", "1")
	t.Setenv("PACMAN_CONFIG_DIR", t.TempDir())
	if err := SaveHighScoreRecord(&HighScoreRecord{Name: "Leader", Score: 500}); err != nil {
		t.Fatalf("seed leaderboard: %v", err)
	}

	g := New()
	g.audio = nil
	g.enteringName = false
	g.playerName = "Winner"
	g.ghosts = nil
	placeOnlyPellets(g, tm.TilePellet)

	if err := g.Update(); err != nil {
		t.Fatalf("winning update returned an error: %v", err)
	}
	if !g.levelComplete {
		t.Fatal("expected final pellet to complete the level")
	}
	if g.highScore != 500 || g.highScoreName != "Leader" {
		t.Fatalf("global high score changed to %s/%d", g.highScoreName, g.highScore)
	}

	for _, record := range LoadLeaderboard() {
		if record.Name == "Winner" && record.Score == pelletPoints {
			return
		}
	}
	t.Fatal("winning player's score was not added below the global high score")
}

func newCompletionTestGame(t *testing.T) *Game {
	t.Helper()
	t.Setenv("PACMAN_DISABLE_AUDIO", "1")
	t.Setenv("PACMAN_CONFIG_DIR", t.TempDir())

	g := New()
	g.audio = nil
	g.enteringName = false
	g.playerName = "Winner"
	g.ghosts = nil
	g.player.CurrentDir = entities.DirNone
	g.player.DesiredDir = entities.DirNone
	return g
}

func placeOnlyPellets(g *Game, pellets ...tm.Tile) {
	for y := range g.tileMap.Tiles {
		for x, tile := range g.tileMap.Tiles[y] {
			if tile == tm.TilePellet || tile == tm.TilePower {
				g.tileMap.Tiles[y][x] = tm.TileEmpty
			}
		}
	}

	gx, gy := g.playerGrid()
	g.tileMap.Tiles[gy][gx] = pellets[0]
	if len(pellets) == 1 {
		return
	}

	for y := range g.tileMap.Tiles {
		for x, tile := range g.tileMap.Tiles[y] {
			if (x != gx || y != gy) && tile != tm.TileWall {
				g.tileMap.Tiles[y][x] = pellets[1]
				return
			}
		}
	}
}
