# LLM expert union

Upperleveled "mixture of experts" approach without router and LLM architecture changing.

This is a simple experiment for achieving better LLM response quality by using multiple LLMs and a simple union of their responses.

## Idea

Simple example: when you want to diagnose a disease, you can ask multiple doctors and get their opinions. Then you can combine these opinions to find the repeating answers and get the most probable diagnosis.

Here's the same idea, but for LLMs. You can ask multiple LLMs the same question and combine their agreements to get the most probable answer.

## Current implementation

Here's only the simpliest implementation using only 1 LLM, but with many experts defined in role-prompts (`sandbox/expert_roles.yml`).

Seems like it works well (but not too good), but I need to perform some benchmarks to be sure. Interesting fact: final expert role very often chooses really correct answer, even if other experts disagree with it.

TODO:

- [x] 1 LLM & multi roles pipeline
- [ ] find little and suitable benchmark
- [ ] perform benchmark on 1-LLM pipeline
- [ ] implement multi-LLM support
  - [ ] benchmark it
