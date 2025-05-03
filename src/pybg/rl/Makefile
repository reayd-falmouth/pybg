NUM := 5000

play_rl:
	@poetry run python play.py $(ARGS)

play_sarsa:
	@poetry run python sarsa_play.py

train_rl:
	@poetry run python train.py -e $(NUM)

train_sarsa:
	@echo "Started at: $$(date)"
	@start=$$(date +%s); \
	poetry run python sarsa_train.py --games $(NUM) --name models/sarsa-vs_random.pkl; \
	end=$$(date +%s); \
	echo "Ended at: $$(date)"; \
	duration=$$((end - start)); \
	echo "Total time: $${duration}s"; \
	echo "Time per game: $$(echo "scale=4; $$duration / $(NUM)" | bc)s"
