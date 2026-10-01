import pymupdf


def extract_text_from_pdf(file_path: str) -> dict:
    document = pymupdf.open(file_path)

    pages = []

    for page_number in range(len(document)):
        page = document[page_number]

        text = str(page.get_text("text")).strip()

        pages.append(
            {
                "page_number": page_number + 1,
                "text": text,
            }
        )

    document.close()

    full_text = "\n\n".join(
        page["text"]
        for page in pages
        if page["text"]
    )

    return {
        "total_pages": len(pages),
        "full_text": full_text,
        "pages": pages,
    }