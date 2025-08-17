import pytest
from project import (
    check_usage,
    speechify,
    load_file,
    get_voice,
    mk_audiobook_dir,
    create_path,
)


# 1. Testing function : check_usage
def test_check_usage_args_len():
    """
    Testing function : check_usage
    program must exit if the no of provided sytem arguments isn't exactly 2.
    """
    with pytest.raises(SystemExit):
        check_usage(["project.py"])
        check_usage(["project.py", "book.txt", "audiobook.mp3"])


def test_check_usage_Invalid_file_format():
    """
    Testing function : check_usage
    Testing Weather the provided file format is '.txt'
    """
    with pytest.raises(SystemExit):
        check_usage(["project.py", "book.pdf"])
        check_usage(["project.py", "book.epub"])
        check_usage(["project.py", "book.mobi"])


def test_check_usage_non_existent_book():
    with pytest.raises(SystemExit):
        check_usage(["project.py", "test_cases/book.txt"])


def test_check_usage_empty_book():
    with pytest.raises(SystemExit):
        check_usage(["project.py", "test_cases/book1.txt"])


def test_check_usage_non_empty_book():
    assert check_usage(["project.py", "test_cases/book2.txt"]) == "test_cases/book2"


# 2. Testing function : load_file
def test_load_file_simple_chapter_structure():
    """
    Test Case 2:
        input: a Book structured into chapters
        output: A list of dicts , each dict is a chapter with 2 key value pairs, one for title , one for chapter content.
    """
    assert load_file("test_cases/book2.txt") == [
        {
            "title": "Chapter 1\n",
            "content": "This is the first chapter.\nIt has two lines.\n\n",
        },
        {
            "title": "Chapter 2\n",
            "content": "Second chapter starts here.\nStill going...\n\n",
        },
        {"title": "Chapter 3\n", "content": "Third chapter's content is here.\n"},
    ]


def test_load_file_book_with_foreword():
    assert load_file("test_cases/book3.txt") == [
        {"title": "Chapter 1\n", "content": "Chapter one content here.\n\n"},
        {"title": "Chapter 2\n", "content": "Chapter two content here.\n"},
    ]

def test_book_with_no_chapters():
    """
    Output must be just one string.
    """
    assert load_file("test_cases/book4.txt") == [
        "This is a short book.\nIt has no chapters at all.\nIt's just text from start to finish.\n"
    ]


# 3. Testing function : create_path
def test_create_path():
    assert create_path("path", "Chapter 1") == "./path/Chapter 1.mp3"
    assert create_path("path", "\n Chapter 1  \n") == "./path/Chapter 1.mp3"
    assert create_path("path", "Chapter 1.") == "./path/Chapter 1.mp3"
