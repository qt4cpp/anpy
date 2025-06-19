import json
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional


@dataclass
class Card:
    question: str
    answer: str
    interval: int = 1
    repetition: int = 0
    due: str = datetime.now().strftime("%Y-%m-%d")

    def schedule(self, correct: bool) -> None:
        today = datetime.now().date()
        if correct:
            self.repetition += 1
            if self.repetition == 1:
                self.interval = 1
            else:
                self.interval *= 2
        else:
            self.repetition = 0
            self.interval = 1
        next_due = today + timedelta(days=self.interval)
        self.due = next_due.strftime("%Y-%m-%d")


class SRS:
    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self.cards: List[Card] = []
        self.load()

    def load(self) -> None:
        if self.path.exists():
            data = json.loads(self.path.read_text())
            self.cards = [Card(**c) for c in data]
        else:
            self.cards = []

    def save(self) -> None:
        self.path.write_text(json.dumps([asdict(c) for c in self.cards], ensure_ascii=False, indent=2))

    def add_card(self, question: str, answer: str) -> None:
        self.cards.append(Card(question=question, answer=answer))
        self.save()

    def due_cards(self) -> List[Card]:
        today = datetime.now().date()
        return [c for c in self.cards if datetime.strptime(c.due, "%Y-%m-%d").date() <= today]

    def update_card(self, card: Card, correct: bool) -> None:
        card.schedule(correct)
        self.save()

    def next_due(self) -> Optional[Card]:
        due = self.due_cards()
        return due[0] if due else None
