from lifesaver_lite_llm.core.tags import tag_flow


def test_tag_flow_basic():
    rec = {
        "input_text": "Let's think step by step. Use the tool to search.",
        "output_text": "",
        "tokens_out": 0,
    }
    tags = tag_flow(rec)
    assert "reasoning" in tags
    assert "tooling" in tags or "retrieval" in tags


def test_tag_flow_multimodal_and_fewshot():
    rec = {
        "input_text": "Example 1: Input: hi Output: ok. Describe image.",
        "output_text": "",
        "tokens_out": 12,
    }
    tags = tag_flow(rec)
    assert "fewshot" in tags
    assert "multimodal" in tags
    assert "generation" in tags
