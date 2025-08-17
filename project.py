import edge_tts
import asyncio
import sys
import re
import os
from tqdm import tqdm


def main():
    book_title = check_usage(sys.argv)
    speechify(load_file(sys.argv[1]), book_title)

def check_usage(args) -> str:
    if len(args) != 2:
        sys.exit("Usage: project.py book.txt")

    book_title, file_format = args[1].split(".")

    if file_format != "txt":
        sys.exit("Usage: project.py book.txt")
    elif not os.path.exists(args[1]):
        sys.exit("The Book you provided doesn't exist.")
    elif os.path.getsize(args[1]) == 0:
        sys.exit("The Book you provided is empty.")

    while os.path.exists(book_title):
        tqdm.write(f"A folder called {book_title} already exists.")
        book_title = input("What would you like to name the audiobook? ")

    return book_title

def load_file(filename: str) -> list:
    # Opening the Book
    try:
        with open(filename) as file:
            lines = file.readlines()
    except Exception as e:
        sys.exit(f"failed to open {filename}")
    book_as_str = ""
    for line in lines:
        book_as_str += f"{line}"

    # structureing the book

    # toc and chapter patterns
    toc_pattern = r"Contents\s*(Chapter[^\n]+)"
    chapter_pattern = r"(Chapter\s(?:[a-z]|\d)+(?:\.|:|\n))\s*(.*?)(?=Chapter\s(?:[a-z]|\d)+(?:\.|:|\n)|\Z)"

    toc_matches = re.finditer(
        toc_pattern,
        book_as_str,
        flags=re.DOTALL | re.IGNORECASE,
    )
    if not re.search(toc_pattern, book_as_str, flags=re.DOTALL | re.IGNORECASE):
        book_contents = book_as_str
    for toc_match in toc_matches:
        first_chapter = re.sub(r"\s+", " ", toc_match.group(1))
        book_stripped = re.sub(r"\s+", " ", book_as_str)

        m = re.finditer(first_chapter, book_stripped, flags=re.DOTALL | re.IGNORECASE)
        # for chapter_one in m:
        m_list = list(m)
        book_contents = book_as_str[m_list[1].start() :]
    # (Chapter (?:[a-z]+|[\d]+)(?:\.|\:|\n))\n?([\w^\n])+\n(.+)
    chapter_matches = re.finditer(
        chapter_pattern,
        book_contents,
        flags=re.DOTALL | re.IGNORECASE,
    )
    if not re.search(chapter_pattern, book_contents, flags=re.DOTALL | re.IGNORECASE):
        return [book_as_str]
    # if chapter matches are found create book as list of chapter dicts
    chapter_titles = []
    chapter_contents = []
    for match in chapter_matches:
        chapter_titles.append(match.group(1))
        chapter_contents.append(match.group(2))

    book_chapters = []
    # check chapters have contents
    if len(chapter_titles) != 0 and len(chapter_contents) == 0:
        sys.exit(
            "Error in Loading: seems like you have provided a Table Of Contents instead of a book."
        )

    for title, content in zip(chapter_titles, chapter_contents):
        chapter = {"title": title, "content": content}
        book_chapters.append(chapter)
    return book_chapters


def speechify(book: list, book_title: str):
    mk_audiobook_dir(book_title)
    voice = asyncio.run(get_voice())
    print(f"\nYou have chosen {voice} to narrate your audiobook.\n")

    # if book isn't structured into chapters
    if len(book) == 1:
        book = {"title": book_title, "content": book}

    async def tts_chapters(book):
        for chapter in tqdm(book, desc="Converting to Audio", unit="chapter"):
            audio_chapter = edge_tts.Communicate(chapter["content"], voice)
            chapter_path = create_path(path=book_title, file_name=chapter["title"])
            try:
                await audio_chapter.save(chapter_path)
            except Exception as e:
                sys.exit(f"Failed to save {chapter['title']} : {e}")
            # print(f"{chapter['title']}mp3 saved")

    asyncio.run(tts_chapters(book))
    return None


async def get_voice():
    voices = await edge_tts.list_voices()
    chosen_voice = input("What voice would you like to narrate your audiobook? ")
    if not chosen_voice:
        # seting default to fall back on
        chosen_voice = "en-US-GuyNeural"
    voice_names = [voice["ShortName"] for voice in voices]
    while chosen_voice not in voice_names:

        print("The voice you provided isn't available. ")
        try:
            chosen_voice = input("Choose Another voice: ")
            if not chosen_voice:
                # seting default to fall back on
                chosen_voice = "en-US-GuyNeural"
        except KeyboardInterrupt:
            sys.exit()

    return chosen_voice


def mk_audiobook_dir(book_title: str):
    try:
        os.mkdir(book_title)
    except FileExistsError:
        sys.exit("A Directory with the same name already exists.")
    except FileNotFoundError:
        sys.exit("The path provided wasn't accessible.")
    except OSError as e:
        sys.exit(f"Directory creation failed error: {e}")
    except PermissionError:
        sys.exit(f"You don't have permission to create directory")
    else:
        return


def create_path(path: str, file_name: str) -> str:
    file_name =file_name.strip()
    if not file_name.endswith("."):
        file_name = file_name + "."
    return f"./{path}/{file_name}mp3"


if __name__ == "__main__":
    main()
