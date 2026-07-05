// #ai-assisted with OCA/OpenAI Model with human supervision

package game

import (
	"math"
	"testing"

	"pacman/internal/entities"
)

func TestMovementConfiguration(t *testing.T) {
	tests := []struct {
		name string
		got  float64
		want float64
	}{
		{name: "player pixels per second", got: playerSpeedPixelsPerSecond, want: 120},
		{name: "player pixels per update", got: playerSpeedPixelsPerUpdate, want: 2},
		{name: "ghost pixels per second", got: ghostSpeedPixelsPerSecond, want: 105},
		{name: "ghost pixels per update", got: ghostSpeedPixelsPerUpdate, want: 1.75},
		{name: "alignment threshold", got: alignmentThreshold, want: 4},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			if test.got != test.want {
				t.Fatalf("got %v, want %v", test.got, test.want)
			}
		})
	}
	if updatesPerSecond != 60 {
		t.Fatalf("updates per second = %d, want 60", updatesPerSecond)
	}
}

func TestVerticalTurnsRespondBeyondAlignmentThreshold(t *testing.T) {
	tests := []struct {
		name       string
		approach   entities.Direction
		turn       entities.Direction
		startDelta float64
	}{
		{name: "approach right turn up", approach: entities.DirRight, turn: entities.DirUp, startDelta: -6},
		{name: "approach left turn up", approach: entities.DirLeft, turn: entities.DirUp, startDelta: 6},
		{name: "approach right turn down", approach: entities.DirRight, turn: entities.DirDown, startDelta: -6},
		{name: "approach left turn down", approach: entities.DirLeft, turn: entities.DirDown, startDelta: 6},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			game := newMovementTestGame(t)
			gridX, gridY := findHorizontalIntersection(t, game, test.turn, false)
			centerX, centerY := game.cellCenter(gridX, gridY)
			game.player.X = centerX + test.startDelta
			game.player.Y = centerY
			game.player.CurrentDir = test.approach
			game.player.DesiredDir = test.turn

			for update := 0; update < 3 && game.player.CurrentDir != test.turn; update++ {
				game.updatePlayerMovement()
			}

			if game.player.CurrentDir != test.turn {
				t.Fatalf("player did not turn %v from %v within 3 updates", test.turn, test.approach)
			}
			if math.Abs(game.player.X-centerX) > 0.001 {
				t.Fatalf("vertical turn did not snap X to center: got %.3f want %.3f", game.player.X, centerX)
			}
			if test.turn == entities.DirUp && game.player.Y >= centerY {
				t.Fatalf("up turn did not move upward: got Y %.3f from %.3f", game.player.Y, centerY)
			}
			if test.turn == entities.DirDown && game.player.Y <= centerY {
				t.Fatalf("down turn did not move downward: got Y %.3f from %.3f", game.player.Y, centerY)
			}
		})
	}
}

func TestVerticalTurnsRejectWalls(t *testing.T) {
	for _, turn := range []entities.Direction{entities.DirUp, entities.DirDown} {
		t.Run(directionName(turn), func(t *testing.T) {
			game := newMovementTestGame(t)
			gridX, gridY := findHorizontalIntersection(t, game, turn, true)
			centerX, centerY := game.cellCenter(gridX, gridY)
			game.player.X = centerX
			game.player.Y = centerY
			game.player.CurrentDir = entities.DirRight
			game.player.DesiredDir = turn

			game.updatePlayerMovement()

			if game.player.CurrentDir == turn {
				t.Fatalf("player turned %s into a wall", directionName(turn))
			}
		})
	}
}

func newMovementTestGame(t *testing.T) *Game {
	t.Helper()
	t.Setenv("PACMAN_DISABLE_AUDIO", "1")
	t.Setenv("PACMAN_CONFIG_DIR", t.TempDir())
	return New()
}

func findHorizontalIntersection(t *testing.T, game *Game, turn entities.Direction, targetWall bool) (int, int) {
	t.Helper()
	_, turnDeltaY := entities.DirDelta(turn)
	for gridY := 1; gridY < game.tileMap.Height-1; gridY++ {
		for gridX := 1; gridX < game.tileMap.Width-1; gridX++ {
			if game.tileMap.IsWall(gridX, gridY) || game.tileMap.IsWall(gridX-1, gridY) || game.tileMap.IsWall(gridX+1, gridY) {
				continue
			}
			isTargetWall := game.tileMap.IsWall(gridX, gridY+turnDeltaY)
			if isTargetWall == targetWall {
				return gridX, gridY
			}
		}
	}
	t.Fatalf("no horizontal intersection found for turn=%s targetWall=%t", directionName(turn), targetWall)
	return 0, 0
}

func directionName(direction entities.Direction) string {
	switch direction {
	case entities.DirUp:
		return "up"
	case entities.DirDown:
		return "down"
	case entities.DirLeft:
		return "left"
	case entities.DirRight:
		return "right"
	default:
		return "none"
	}
}
