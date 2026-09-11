import 'package:flutter_test/flutter_test.dart';

import 'package:flutter_2048/models/board.dart';
import 'package:flutter_2048/models/tile.dart';

void main() {
  test('board JSON round-trip preserves game state', () {
    final board = Board(
      128,
      1024,
      [Tile('tile-1', 64, 7, merged: true)],
      won: false,
      over: false,
    );

    final restored = Board.fromJson(board.toJson());

    expect(restored.score, 128);
    expect(restored.best, 1024);
    expect(restored.tiles.single.id, 'tile-1');
    expect(restored.tiles.single.value, 64);
    expect(restored.tiles.single.index, 7);
    expect(restored.tiles.single.merged, isTrue);
  });

  test('tile positioning maps board indexes onto a four-column grid', () {
    final tile = Tile('tile-1', 2, 5);

    expect(tile.getTop(64), 88);
    expect(tile.getLeft(64), 88);
  });
}
