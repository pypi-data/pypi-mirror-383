from collections import namedtuple
import re
from bs4 import (
    BeautifulSoup,
    Comment,
    Doctype,
    ProcessingInstruction,
    MarkupResemblesLocatorWarning,
)
import logging
import copy
import json
import warnings

warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)


# All of the valid operations we can perform and translate to ADF
VALID_PARTS = [
    ("<html>", "</html>", "html"),
    ("<head>", "</head>", "heading1"),
    ("<title>", "</title>", "heading1"),
    ("<body>", "</body>", "body"),
    ("<div>", "</div>", "paragraph"),
    ("<h1>", "</h1>", "heading1"),
    ("<h2>", "</h2>", "heading2"),
    ("<h3>", "</h3>", "heading3"),
    ("<h4>", "</h4>", "heading4"),
    ("<h5>", "</h5>", "heading5"),
    ("<h6>", "</h6>", "heading6"),
    ("<p>", "</p>", "paragraph"),
    ("<table>", "</table>", "tablebase"),
    ("<thead>", "</thead>", "tablehead"),
    ("<tbody>", "</tbody>", "tablebody"),
    ("<th>", "</th>", "tablecell"),
    ("<tr>", "</tr>", "tablerow"),
    ("<td>", "</td>", "tablecell"),
    ("<b>", "</b>", "strong"),
    ("<strong>", "</strong>", "strong"),
    ("<i>", "</i>", "em"),
    ("<em>", "</em>", "em"),
    ("<s>", "</s>", "strike"),
    ("<u>", "</u>", "underline"),
]

# This is aimed at a simple test-for-word-inside
# We check if the type contains the following to validate if it's a container_type object
CONTAINER_TYPES = {
    "paragraph",
    "head",
    "table",
    "html",
    "body",
}

# modifier type of nodes
modifiers = {"strong", "em", "strike", "underline"}

# This just wraps up what I define as a container type, by matching if it has head, paragraph, or table in the valid_part
all_container_types = [
    vpart for cont in CONTAINER_TYPES for vpart in VALID_PARTS if cont in vpart[2]
]


# Extracts valid tags from valid_parts
def extract_valid_tags(valid_parts):
    tags = set()
    for part in valid_parts:
        items = part
        for item in items:
            if not isinstance(item, str):
                continue

            _match = re.search(r"<\s*/?\s*([a-zA-Z0-9:-]+)", item)
            if _match:
                tags.add(_match.group(1).lower())
            else:
                tags.add(item.strip().lower())
    return tags


# Marshals our incoming html to something we can parse
def sanitize_html(html: str, valid_parts):
    html = html.replace("<br>", "\n")
    allowed = extract_valid_tags(valid_parts)
    sanitizer_special_tags = {"<a>"}

    allowed |= sanitizer_special_tags

    soup = BeautifulSoup(html, "html.parser")

    for link in soup.find_all("a"):
        href = link.get("href", "")
        encoded_text = f'~y~href="{href}"~y~~z~{link.get_text()}~z~'
        link.replace_with(encoded_text)

    # Throw out comments, docstrings and spans
    for el in soup.find_all(string=True):
        if isinstance(el, (Comment, Doctype, ProcessingInstruction)):
            el.extract()

    # Delete anything we don't want
    for bad in soup.find_all(["script", "style"]):
        bad.decompose()

    # Find all of our tags and go through them
    for tag in soup.find_all(True):
        name = tag.name.lower()
        if name not in allowed:
            tag.unwrap()  # Instead of decompose, we unwrap to keep the content
            continue
        tag.attrs.clear()

    # Remove nested empty structures
    def is_effectively_empty(tag):
        if not tag.get_text(strip=True):
            return True
        if tag.find_all(True) and all(
            is_effectively_empty(child) for child in tag.find_all(True)
        ):
            return True
        return False

    # Multiple passes to handle nested structures
    for _ in range(3):
        for tag in soup.find_all(["table", "tbody", "th", "tr", "td", "div"]):
            if is_effectively_empty(tag):
                tag.decompose()

    # get all lite container types, and remove our < and > to play nice with bs
    all_container_lites = [
        cont[0].replace("<", "").replace(">", "")
        for cont in all_container_types
        if cont[0]
        not in [
            "<thead>",
            "<tbody>",
            "<table>",
            "<tr>",
            "<td>",
            "<th>",
            "<html>",
            "<body>",
        ]
    ]

    # Final pass: convert remaining divs to paragraphs and remove empty tags
    for tag in soup.find_all(True):
        if tag.name.lower() == "head":
            if tag.title:
                title_text = tag.title.get_text(strip=True)
                tag.clear()
                tag.append(title_text)

        if tag.name.lower() == "div":
            if tag.get_text(strip=True):
                uwrapped: bool = False
                for _c_node in tag.children:
                    if _c_node.name in all_container_lites:
                        tag.unwrap()
                        uwrapped: bool = True

                if not uwrapped:
                    tag.name = "p"
            else:
                tag.decompose()
                continue
        elif not tag.contents or (not tag.get_text(strip=True) and not tag.find(True)):
            tag.decompose()
            continue

        # clean up any nested container_lites
        if any(True for _cont in all_container_lites if tag.name.lower() == _cont):
            for inner in tag.find_all(all_container_lites):
                inner.unwrap()
    sanitized = (
        str(soup).replace("\n", "\n\n").replace("            ", "").replace("\r", "")
    )

    return sanitized


class Part:
    """
    Part is a object which contains a 'part' of an adf document
    """

    def __init__(self, type_of_node="", text=""):
        self.type_of_node = type_of_node
        self.text = text
        self.inner_parts = []
        self.marks = set()
        # It gets all the existing marks in a set and the cleaned up text without the marks.

    def propagate_parent_marks_downwards(self):
        """
        propagate current marks downwards, if we're a text part with children, since html follows a top-down schema
        """
        if (
            self.type_of_node == "text"
            or self.type_of_node in modifiers
            and self.inner_parts
        ):
            for child in self.inner_parts:
                if self.type_of_node in modifiers:
                    self.marks.add(self.type_of_node)
                child.marks |= self.marks
                child.propagate_parent_marks_downwards()

    # If text is just floating around in the text field of a non type_of_node=text we can mutate the Part to follow our schema
    def cleanup_flat_text(self):
        if (
            self.type_of_node != "table"
            and any(True for cont in CONTAINER_TYPES if cont in self.type_of_node)
            or self.type_of_node == "disconnected_text"
        ):
            if self.text:
                self.text = self.clear_all_disconnected_marks()

                _subpart_marks_and_text = self.get_marks_and_text()
                _subpart = Part(type_of_node="text", text=_subpart_marks_and_text[1])
                _subpart.marks = _subpart_marks_and_text[0]

                self.inner_parts.append(_subpart)
                self.text = ""

    def get_marks_and_text(self) -> tuple[set, str]:
        text = self.text
        marks = set()
        while any(
            valid_mark[0] in text and valid_mark[1] in text
            for valid_mark in VALID_PARTS
        ):
            # filter out marks and make sure they're not container_types
            for mark in (_m for _m in VALID_PARTS if _m[2]):
                if mark[0] in text and mark[1] in text:
                    s_index = text.find(mark[0])
                    l_index = text.rfind(mark[1])
                    marks.add(mark[2])
                    text = text[s_index + len(mark[0]) : l_index]
        return (marks, text)

    def clear_all_disconnected_marks(self) -> str:
        # Clear all disconnected marks from a string and leave our raw text.
        text = self.text
        while any(
            valid_mark[0] in text and valid_mark[1] not in text
            for valid_mark in VALID_PARTS
        ):
            # filter out marks and make sure they're not container_types
            for mark in (_m for _m in VALID_PARTS):
                if mark[0] in text and mark[1] not in text:
                    s_index = text.find(mark[0])
                    text = text[s_index + len(mark[0]) :]

                if mark[0] in text and mark[1] in text:
                    continue
        while any(
            valid_mark[1] in text and valid_mark[0] not in text
            for valid_mark in VALID_PARTS
        ):
            # filter out marks and make sure they're not container_types
            for mark in (_m for _m in VALID_PARTS):
                if mark[1] in text and mark[0] not in text:
                    s_index = text.find(mark[1])
                    text = text[s_index + len(mark[1]) :]

                if mark[0] in text and mark[1] in text:
                    continue
        return text

    # Drill down all sub-parts and extract their raw text
    def drill_all_text(self):
        txt_result = ""
        if self.inner_parts:
            for i_c in self.inner_parts:
                txt_result += f" {i_c.drill_all_text()}"
        else:
            if self.text:
                txt_result += self.text
        return txt_result.replace("  ", " ")

    def d(self):
        print(self.__dict__)


def find_next_tag(buffer: str, valid_parts: str):
    """Searches for for the earliest opening tag in a string relative to our valid_parts
    Parameters:
        buffer (str): A buffer string to scan over
        valid_parts (List[tuple[str, str, str]]): a List of valid_parts (intro_tag, exit_tag, real_name)
    Returns:
        NextValidPart (object): NextValidPart(open_tag, close_tag, type_of, start_index, end_index, is_container)
        If no match None
    """
    best_match = None
    for open_tag, close_tag, type_of in valid_parts:
        s = buffer.find(open_tag)
        if s == -1:
            continue
        e = buffer.find(close_tag, s + len(open_tag))
        if e == -1:
            continue
        if best_match is None or s < best_match[3]:
            is_container_object = False
            if any([True for ct in CONTAINER_TYPES if ct in type_of]):
                is_container_object = True
            best_match = (open_tag, close_tag, type_of, s, e, is_container_object)
    if best_match:
        NextValidPart = namedtuple(
            "NextValidPart",
            field_names=[
                "open_tag",
                "close_tag",
                "type_of",
                "start_index",
                "end_index",
                "is_container",
            ],
        )
        return NextValidPart(
            best_match[0],
            best_match[1],
            best_match[2],
            best_match[3],
            best_match[4],
            best_match[5],
        )
    else:
        return None


def get_parts(html: str, in_container=False, debug=False) -> list:
    """
    This function is what breaks html off into a structure I can comprehend and translate to ADF

    Essentially if it's an HTML Node in VALID_PARTS, we break the node into container types, modifier types and text nodes.
    This can then be drilled down, depending on the modifiers that occur, allowing for multi-layered recursion fun

    My only rule of thumb, is most container-types except container-lites (html, body, tables) cannot have container-types
    We follow this rule because ADF follows this rule.

    Parameters:
        html (str): Our sanitized HTML
        in_container (bool optional): Used in recursion to decide if we're recursing
        debug (bool optional): Leveraged to help add some output to what's going on internally

    Returns:
        list of parts we've extracted
    """
    if debug:
        logger.debug("____________\nIteration:🕒\n____________\n")

    # Setup our buffer string which we'll carve out
    buffer_str: str = html.strip()

    # Create our intended object to pull per iteration
    parts = []

    first_instance = True
    previous_end_position = 0

    # Loop while we have a buffer_str that hasn't been completely chipped away
    while any(
        _v_part[0] in buffer_str and _v_part[1] in buffer_str for _v_part in VALID_PARTS
    ):
        # ? NextValidPart (object): NextValidPart(open_tag, close_tag, type_of, start_index, end_index, is_container)
        next_valid_part = find_next_tag(buffer=buffer_str, valid_parts=VALID_PARTS)
        if next_valid_part:
            part = Part()

            if first_instance:
                # On first iteration we attempt to catch all of the preamble text, into a paragraph object.
                intro_text = buffer_str[: next_valid_part.start_index]
                if intro_text:
                    _intro_part = Part()
                    _intro_part.text = buffer_str[: next_valid_part.start_index]

                    _intro_part.type_of_node = (
                        "paragraph"
                        if not any(
                            [
                                True
                                for cont in CONTAINER_TYPES
                                if cont in next_valid_part.type_of
                            ]
                        )
                        else next_valid_part.type_of
                    )

                    parts.append(_intro_part)
                first_instance = False
            else:
                # Capture interlude text between tags (not just preamble)
                interlude_text = buffer_str[
                    previous_end_position : next_valid_part.start_index
                ]
                if interlude_text.strip():  # Only create part if there's actual content
                    _interlude_part = Part()
                    _interlude_part.text = interlude_text
                    # Interlude text should always be paragraph type since it wont follow a specific node
                    _interlude_part.type_of_node = "paragraph"
                    parts.append(_interlude_part)

            start_index = next_valid_part.start_index + len(next_valid_part.open_tag)
            end_index = next_valid_part.end_index

            part.type_of_node = (
                next_valid_part.type_of
            )  # Define what type of part this is for look-up and transformation

            part.text = buffer_str[
                start_index:end_index
            ]  # The substringed text content

            # This is the voodoo responsible for drilling down recursively, and iterating over descendent: containers / modifier parts.
            def _walk(origin_part: Part):
                next_tag = find_next_tag(origin_part.text, valid_parts=VALID_PARTS)
                if next_tag:

                    # Recurse:
                    # Get the 3 parts of the document and combine them.
                    _inner_shards = get_document_shards(
                        origin_part.text, in_container=True
                    )
                    for _, _shard_parts in _inner_shards.items():
                        origin_part.inner_parts += _shard_parts

                    if next_tag.is_container:
                        origin_part.text = ""  # ? We do not preserve active start and end text around nodes as our top-level recursion handles that
                    else:
                        for child in origin_part.inner_parts:
                            child.marks.add(origin_part.type_of_node)
                            if child.type_of_node in modifiers:
                                child.marks.add(child.type_of_node)
                                child.marks = child.marks | origin_part.marks

                                # remove non-modifiers from our children
                                non_mod_parts = set()
                                for i in child.marks:
                                    if any(
                                        [True for cont in CONTAINER_TYPES if cont in i]
                                    ):
                                        non_mod_parts.add(i)
                                [child.marks.remove(nmp) for nmp in non_mod_parts]

                            child.type_of_node = "text"

                        origin_part.text = ""

                return origin_part

            part = _walk(part)

            # Update previous_end_position to track where this tag ended
            previous_end_position = 0  # Reset to 0 since we're updating buffer_str
            buffer_str = buffer_str[(end_index + len(next_valid_part.close_tag)) :]

            parts.append(part)
            if debug:
                logger.debug("top_level_iterated part: {}".format(part.__dict__))

    if buffer_str:
        buffer_str = buffer_str.strip()
        if debug:
            logger.debug("LAST invoke of buffer string is: {}".format(buffer_str))
        part = Part()
        part.text = buffer_str
        part.cleanup_flat_text()
        # This is a disconnected_node because the last portion of the buffer isn't any html tags - paragraph might work too
        part.type_of_node = "disconnected_text"
        parts.append(part)

    def clear_standalone_flat_text(part: Part):
        # An optimal structure is any text merged into it's own Part as an inner_part
        # This recurses over the children of our parts, and drills to the bottom.
        _c_part: Part
        for _c_part in part.inner_parts:
            if not _c_part.inner_parts:
                _c_part.cleanup_flat_text()
            clear_standalone_flat_text(_c_part)

    _part: Part
    for _part in parts:
        clear_standalone_flat_text(_part)
        _part.propagate_parent_marks_downwards()

    return parts


def get_document_shards(html: str, in_container=False):
    """
    Hunts through the presented html, and breaks the parts off into what I call document shards.

    This is because the preamble and epilogue are undetectable if we follow traditional html schema
    But due to the ambigious nature of ADF text, we have to compensate for non-standard schemas

    Returns:
        document (dict): {
            "preamble": List[Part] if exists,
            "body": List[Part],
            "epilogue": List[Part] if exists
        }
    """
    doc_start = html.find("<html>")

    shards = {}
    if doc_start != -1 and doc_start != 0 and html.count("<html>") < 2:
        shards["preamble"] = get_parts(html=html[:doc_start], in_container=in_container)

        html = html[doc_start:]
        doc_end = html.find("</html>")

        if doc_end != -1 and doc_end:
            body_html = html[: doc_end + len("</html>")]
        else:
            body_html = html

        shards["body"] = get_parts(html=body_html, in_container=in_container)

        if doc_end != -1 and doc_end + len("</html>") != len(html):
            shards["epilogue"] = get_parts(
                html=html[doc_end + len("</html>") :], in_container=in_container
            )

    else:
        if html.count("<html>") > 2:
            html.replace("<html>", "").replace("</html>", "")
        shards["body"] = get_parts(html=html, in_container=in_container)

    for shard in shards:
        for stand_alone_part in shards[shard]:
            if stand_alone_part.type_of_node in modifiers:
                stand_alone_part.propagate_parent_marks_downwards()
                child_part = Part(type_of_node="text", text=stand_alone_part.text)
                child_part.marks.add(stand_alone_part.type_of_node)

                stand_alone_part.inner_parts.append(child_part)
                stand_alone_part.type_of_node = "disconnected_text"
                stand_alone_part.text = ""

            if not stand_alone_part.inner_parts and stand_alone_part.text:
                stand_alone_part.cleanup_flat_text()
                stand_alone_part.type_of_node = "disconnected_text"

    return shards


# HTML -> ADF conversion function for most text
def generate_adf_text_content(part):
    all_text_blobs = []

    def clearout_link(original_text: str):
        # Clears out text at the detected sanitization strings
        left_most = original_text.find("~y~")
        right_most = original_text.find("~y~", (left_most + 1)) + len("~y~")
        original_text = f"{original_text[:left_most]}{original_text[right_most:]}"

        left_most = original_text.find("~z~")
        right_most = original_text.find("~z~", (left_most + 1)) + len("~z~")
        original_text = f"{original_text[:left_most]} ~x~ {original_text[right_most:]}"
        return original_text

    def convert_to_text_obj(text_content: str):
        # Convert whatever text we have into an adf text object.
        adf_obj = {
            "type": "text",
            "text": text_content,
        }
        return adf_obj

    def get_link_object(href_start, text):
        # Using a link index and text, we create an adf link object out of the text going left to right for our santized delimiters
        if text.find("~z~") == -1 and text.find("~y~") == -1 and href_start == -1:
            link_content = {"type": "text", "text": text, "marks": {}}
            link_type = {
                "type": "link",
                "attrs": {
                    "href": text,
                },
            }
            link_content["marks"] = [link_type]
            return link_content

        link_start = href_start + len('~y~href="')
        link = text[link_start:]
        link = link[: link.find('"~y~')]
        href_end = text.find('"~y~', link_start) + len('"~y~')

        # Substring out our delimiter
        text = text[:href_start] + text[href_end:]

        msg_start = text.find("~z~")
        msg = text[(msg_start + len("~z~")) :]
        msg = msg[: msg.find("~z~")]

        link_content = {"type": "text", "text": msg, "marks": {}}

        link_type = {
            "type": "link",
            "attrs": {
                "href": link if link else text,
            },
        }

        link_content["marks"] = [link_type]
        return link_content

    def recursive_content_generation(child: Part):
        content = {
            "type": "text",
            "text": child.drill_all_text(),
        }

        # If we encounter a link we have to restructure the entire text to compensate
        independent_link_content = None
        inner_content = []

        # If a mark is not a container_type, wrap it into an adf style object
        valid_marks = [
            {"type": mark}
            for mark in child.marks
            if not any(mark in cont[2] for cont in all_container_types) and child.marks
        ]

        if "https://" in content["text"] or "http://" in content["text"]:
            # The ~y~ is our custom encoding that the sanitizer sprinkles in replacement for <a> links, so we can leverage the href
            href_start = content["text"].find('~y~href="')

            # If we didn't sanitize the string with our delimiters, we just treat the whole thing as a link.
            if href_start == -1:
                link_content = get_link_object(
                    href_start=href_start, text=content["text"]
                )
                inner_content.append(link_content)
            else:
                while href_start != -1:
                    # add the length of our cutter
                    independent_link_content = get_link_object(
                        href_start=href_start,
                        text=content["text"],
                    )

                    split_content = clearout_link(content["text"]).split("~x~")

                    inner_content.append(split_content[0])
                    inner_content.append(independent_link_content)
                    content["text"] = split_content[1]
                    href_start = content["text"].find('~y~href="')

                # Throw the tail remainder on
                if content["text"]:
                    inner_content.append(content["text"])

        if inner_content:
            for cont in inner_content:
                if isinstance(cont, str):
                    cont = cont.replace("  ", " ")
                    cont = convert_to_text_obj(cont)
                if valid_marks:
                    if cont.get("marks"):
                        cont["marks"] += valid_marks
                    else:
                        cont["marks"] = valid_marks
                all_text_blobs.append(cont)
        else:
            if valid_marks:
                content["marks"] = valid_marks

            all_text_blobs.append(content)

    for child in part.inner_parts:
        if child.inner_parts:
            for inner_mod_child in child.inner_parts:
                recursive_content_generation(child=inner_mod_child)
        else:
            recursive_content_generation(child=child)

    for txt in all_text_blobs:
        if txt["text"] == "":
            txt["text"] = " "

    return all_text_blobs


# HTML -> ADF conversion function for paragraphs
def construct_paragraph_blob(part: Part) -> dict:
    resulting_type = {
        "type": "paragraph",
        "content": [],
    }
    if part.text and part.type_of_node == "paragraph" and not part.inner_parts:
        part.cleanup_flat_text()
    resulting_type["content"] = generate_adf_text_content(part)
    return resulting_type


# HTML -> ADF conversion function for headers
def construct_heading_blob(part: Part) -> dict:
    name_index = part.type_of_node.find("heading") + len("heading")
    level = part.type_of_node[name_index:]
    resulting_type = {
        "type": "heading",
        "attrs": {"level": int(level)},  # not required
        "content": [],  # not required, applicable only in containers
    }

    resulting_type["content"] = generate_adf_text_content(part=part)

    return resulting_type


# HTML -> ADF conversion function for tables
def construct_table_blob(part: Part) -> dict:
    resulting_type = {
        "type": "table",
        "content": [],
    }
    
    table_content = []

    row_template = {
        "type": "tableRow",
        "content": [],
    }

    # template for structure marshalling
    inner_template = {
        "type": "",
        "content": [],
    }

    malformed_structure = False

    if len(part.inner_parts) == 1 and "tablehead" not in [
        part.inner_parts[0].type_of_node
    ]:
        malformed_structure = True

    known_dimensionsf = False
    row_dimensions = 0
    current_cell = 0

    if not malformed_structure:
        for table_top in part.inner_parts:

            row_t = copy.deepcopy(row_template)
            cell_t = copy.deepcopy(inner_template)

            if table_top.type_of_node == "tablehead":
                cell_t["type"] = "tableHeader"
            else:
                cell_t["type"] = "tableCell"

            inner_content = []
            # iterate through each 'row' in our table
            for table_row in table_top.inner_parts:
                if table_row.type_of_node == "tablerow":
                    for cell in table_row.inner_parts:
                        cell_t["content"] = [unwrap_part_to_adf_type(cell)]

                        # dynamically define our dimensions
                        if cell_t["type"] == "tableHeader":
                            row_dimensions += 1
                            known_dimensionsf = True
                        # mark each indice
                        if cell_t["type"] == "tableCell":
                            current_cell += 1

                        # Default supply content to our middle table
                        inner_content.append(copy.deepcopy(cell_t))
                        if known_dimensionsf and current_cell == row_dimensions:
                            new_row = copy.deepcopy(row_template)
                            current_row_cells = []
                            
                            for item in inner_content:
                                current_row_cells.append(item)
                            inner_content.clear()

                            new_row["content"] = current_row_cells
                            table_content.append(copy.deepcopy(new_row))
                            current_cell = 0
                else:
                    logger.error(
                        "[html_to_adf] -> error we've bumped into a non_table_row inside a table?? {}".format(
                            table_row.type_of_node
                        )
                    )

            row_t["content"] = inner_content
            table_content.append(copy.deepcopy(row_t))

    if malformed_structure:
        for table_row in part.inner_parts[0].inner_parts:
            row_t = copy.deepcopy(row_template)
            row_content = []

            for cell in table_row.inner_parts:
                cell_t = copy.deepcopy(inner_template)
                cell_t["type"] = "tableCell"
                cell_t["content"] = [unwrap_part_to_adf_type(cell)]
                row_content.append(cell_t)

            row_t["content"] = [*row_content]

            table_content.append(copy.deepcopy(row_t))
    else:
        table_content.pop()  # Remove our template

    resulting_type["content"] = [*table_content]

    return resulting_type


# HTML -> ADF conversion function for bodies
def construct_body_content(part: Part) -> dict:
    content = []
    for sub_part in part.inner_parts:
        content.append(unwrap_part_to_adf_type(sub_part))
    return content


def unwrap_part_to_adf_type(part: Part) -> dict | list:
    """
    Takes in a Part, and translates that part into ADF via it's type_of_node property
    ```
        Example of output
            resulting_type = {
                "type": "",
                "content": "",  # not required, applicable only in containers
                "attrs": "",  # not required
                "marks": "",  # not required
            }
    ```

    Parameters:
        part (Part): The Part we're looking to translate to ADF.

    Returns:
        An ADF formatted dict
        or a list of ADF formatted dicts (only if we construct a Major node, like a body or html)
    """
    try:
        type_comparisons = {
            "paragraph": construct_paragraph_blob,
            "heading": construct_heading_blob,
            "heading1": construct_heading_blob,
            "heading2": construct_heading_blob,
            "heading3": construct_heading_blob,
            "heading4": construct_heading_blob,
            "heading5": construct_heading_blob,
            "heading6": construct_heading_blob,
            "tablecell": construct_paragraph_blob,
            "disconnected_text": construct_paragraph_blob,
            "body": construct_body_content,
            "html": construct_body_content,
            "text": generate_adf_text_content,  # shouldn't get hit?
            "tablebase": construct_table_blob,
        }
        adf_content: dict = type_comparisons[part.type_of_node](part)
    except Exception as ex:
        logger.error(
            "[html_to_adf - unwrap_part_to_adf_type] -> error unwrapping: {}\n{}".format(
                part.__dict__,
                ex
            )
        )
    return adf_content


def join_document_shards(shards: list[list]) -> dict:
    """
    Joins multiple document shards to a combined document

    Document shards are segmented into 3 possible parts ['preamble'], ['body'], ['epilogue']

    Parameters:
        shards (list[list]) - Our shards hopefully retrieved from get_document_shards()

    Returns:
        An ADF document (dict)
    """

    def merge_disconnected_parts(_parts):
        # Process right-to-left, since it makes merging easier
        merged_parts = []
        i = len(_parts) - 1

        while i >= 0:
            current_part = _parts[i]

            if current_part.type_of_node == "disconnected_text":
                # Start a new merged part - preserve disconnected_text type
                merged_part = Part("disconnected_text", "")
                merged_part.inner_parts.extend(current_part.inner_parts)

                # Look backwards for more consecutive disconnected_text parts
                j = i - 1
                while j >= 0 and _parts[j].type_of_node == "disconnected_text":
                    # Prepend the inner_parts (since we're going backwards)
                    merged_part.inner_parts = (
                        _parts[j].inner_parts + merged_part.inner_parts
                    )
                    j -= 1

                merged_parts.append(merged_part)
                i = j  # Skip all the parts we just merged
            else:
                merged_parts.append(current_part)
                i -= 1
        return merged_parts

    document = {
        "body": {
            "version": 1,
            "type": "doc",
            "content": [],
        },
    }

    preamble_parts = shards.get("preamble")
    if preamble_parts:
        merged_parts = merge_disconnected_parts(preamble_parts)
        # Reverse the list since we built it backwards
        shards["preamble"] = list(reversed(merged_parts))

    # repeat the same for epilogue parts
    epilogue_parts = shards.get("epilogue")
    if epilogue_parts:
        merged_parts = merge_disconnected_parts(epilogue_parts)
        shards["epilogue"] = list(reversed(merged_parts))

    # repeat the same for body
    body_parts = shards.get("body")
    if body_parts:
        merged_parts = merge_disconnected_parts(body_parts)
        shards["body"] = list(reversed(merged_parts))

    for shard_type in shards:
        for sub_parts in shards[shard_type]:
            resulting_list = []
            adf_sub_doc = unwrap_part_to_adf_type(sub_parts)

            # Preambles and epilogues follow this
            if isinstance(adf_sub_doc, dict):
                resulting_list.append(adf_sub_doc)

            if isinstance(adf_sub_doc, list):

                for item in adf_sub_doc:
                    if isinstance(item, list):
                        resulting_list += item
                    if isinstance(item, dict):
                        resulting_list.append(item)
            document["body"]["content"] += resulting_list

    return document


def convert_html_to_adf(html: str, output_request_structure=False) -> dict | None:
    """Primary function of this helper, this converts any provided html-to-adf so long as it falls in the confines of `VALID_PARTS`

    Parameters:
        html (str): Any html formatted text, preferably not malformed or we may just reject it.
        output_request_structure (bool): Do we want the structure to be 'request' payload friendly (keep 'body': {})

    Returns:

    """
    try:
        # Sanitize incoming html
        sanitized_html = sanitize_html(html, VALID_PARTS)

        # Branch each segment of html into it's own context
        document_shards = get_document_shards(html=sanitized_html)

        # Join each document segment together and unify into an adf document
        document = join_document_shards(document_shards)

        if not output_request_structure:
            return document["body"]
    except Exception as ex:
        logger.error(
            "[html_to_adf] -> Error occurred trying to parse html to adf: {}".format(
                ex
            ),
            exc_info=True,
        )
        return None
    return document


def export_document(document):
    with open("output.json", "w") as f:
        json.dump(document, f, indent=2)


def import_html_to_str(name):
    html = ""
    with open(name, "r") as f:
        html = f.read()
    return html
