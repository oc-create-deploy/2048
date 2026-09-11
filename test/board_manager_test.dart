import 'dart:io';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_swipe_detector/flutter_swipe_detector.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hive/hive.dart';

import 'package:flutter_2048/managers/board.dart';
import 'package:flutter_2048/models/board.dart';
import 'package:flutter_2048/models/board_adapter.dart';
import 'package:flutter_2048/models/tile.dart';

void main() {
  late Directory hiveDirectory;

  setUp(() async {
    hiveDirectory =
        await Directory.systemTemp.createTemp('board_manager_test_');
    Hive.init(hiveDirectory.path);
    if (!Hive.isAdapterRegistered(0)) {
      Hive.registerAdapter(BoardAdapter());
    }
  });

  tearDown(() async {
    await Hive.close();
    if (hiveDirectory.existsSync()) {
      hiveDirectory.deleteSync(recursive: true);
    }
  });

  Future<(ProviderContainer, BoardManager)> load(Board board) async {
    final box = await Hive.openBox<Board>('boardBox');
    await box.add(board);
    final container = ProviderContainer();
    final manager = container.read(boardManager.notifier);
    for (var attempt = 0;
        attempt < 20 &&
            !container
                .read(boardManager)
                .tiles
                .any((tile) => tile.id == board.tiles.first.id);
        attempt++) {
      await Future<void>.delayed(const Duration(milliseconds: 5));
    }
    return (container, manager);
  }

  test('a 2 + 2 merge adds the merged value to the score', () async {
    final (container, manager) = await load(
      Board(10, 20, [Tile('a', 2, 0), Tile('b', 2, 1)]),
    );
    addTearDown(container.dispose);

    manager.move(SwipeDirection.left);
    manager.merge();

    final state = container.read(boardManager);
    expect(state.score, 14);
    expect(state.tiles.where((tile) => tile.value == 4), hasLength(1));
  });

  test('new game keeps the higher best score and starts with two tiles',
      () async {
    final (container, manager) = await load(
      Board(128, 64, [Tile('a', 2, 0)]),
    );
    addTearDown(container.dispose);

    manager.newGame();

    final state = container.read(boardManager);
    expect(state.best, 128);
    expect(state.score, 0);
    expect(state.tiles, hasLength(2));
    expect(state.tiles.map((tile) => tile.index).toSet(), hasLength(2));
  });

  test('move does not mutate the previous board used for undo', () async {
    final originalTiles = [Tile('a', 2, 3), Tile('b', 4, 0)];
    final (container, manager) = await load(Board(0, 0, originalTiles));
    addTearDown(container.dispose);
    final previousBoard = container.read(boardManager);

    manager.move(SwipeDirection.left);

    expect(previousBoard.tiles.map((tile) => tile.index), [3, 0]);
    expect(container.read(boardManager).undo, same(previousBoard));
    manager.undo();
    expect(
        container.read(boardManager).tiles.map((tile) => tile.index), [3, 0]);
  });
}
