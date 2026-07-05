package tilemap

import "testing"

func TestNewDefaultMapDimensions(t *testing.T) {
	m := NewDefaultMap(16)
	if m.Width != len(defaultMaze[0]) || m.Height != len(defaultMaze) {
		t.Fatalf("unexpected dimensions: got %dx%d, want %dx%d", m.Width, m.Height, len(defaultMaze[0]), len(defaultMaze))
	}
}

func TestEatPelletAt(t *testing.T) {
	m := NewDefaultMap(16)
	var px, py int
	found := false
	for y := 0; y < m.Height && !found; y++ {
		for x := 0; x < m.Width && !found; x++ {
			if m.Tiles[y][x] == TilePellet {
				px, py = x, y
				found = true
			}
		}
	}
	if !found {
		t.Fatal("no pellet found in default map")
	}

	ate, power := m.EatPelletAt(px, py)
	if !ate || power {
		t.Fatalf("expected to eat normal pellet, got ate=%v power=%v", ate, power)
	}
	ate, power = m.EatPelletAt(px, py)
	if ate || power {
		t.Fatalf("expected to not eat after consumed, got ate=%v power=%v", ate, power)
	}
}

func TestIsWallBounds(t *testing.T) {
	m := NewDefaultMap(16)
	if !m.IsWall(-1, 0) || !m.IsWall(0, -1) || !m.IsWall(m.Width, 0) || !m.IsWall(0, m.Height) {
		t.Fatalf("out-of-bounds should be treated as wall")
	}
}

func TestRemainingPelletsCountsRegularAndPowerPellets(t *testing.T) {
	m := &TileMap{
		Width:  3,
		Height: 2,
		Tiles: [][]Tile{
			{TileEmpty, TilePellet, TileWall},
			{TilePower, TileEmpty, TilePellet},
		},
	}

	if got := m.RemainingPellets(); got != 3 {
		t.Fatalf("remaining pellets = %d, want 3", got)
	}
	if ate, power := m.EatPelletAt(1, 0); !ate || power {
		t.Fatalf("eat regular pellet: ate=%v power=%v", ate, power)
	}
	if got := m.RemainingPellets(); got != 2 {
		t.Fatalf("remaining pellets after regular pellet = %d, want 2", got)
	}
	if ate, power := m.EatPelletAt(0, 1); !ate || !power {
		t.Fatalf("eat power pellet: ate=%v power=%v", ate, power)
	}
	if got := m.RemainingPellets(); got != 1 {
		t.Fatalf("remaining pellets after power pellet = %d, want 1", got)
	}
	if ate, power := m.EatPelletAt(2, 1); !ate || power {
		t.Fatalf("eat final regular pellet: ate=%v power=%v", ate, power)
	}
	if got := m.RemainingPellets(); got != 0 {
		t.Fatalf("remaining pellets after final pellet = %d, want 0", got)
	}
}
