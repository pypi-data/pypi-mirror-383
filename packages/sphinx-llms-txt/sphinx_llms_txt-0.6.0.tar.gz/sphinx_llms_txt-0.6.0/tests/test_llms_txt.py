"""Test the sphinx_llms_txt extension."""

from sphinx_llms_txt import (
    DocumentCollector,
    DocumentProcessor,
    FileWriter,
    LLMSFullManager,
    setup,
)


def test_version():
    """Test that the version is defined."""
    from sphinx_llms_txt import __version__

    assert __version__


def test_setup_returns_valid_dict():
    """Test that the setup function returns a valid dict."""

    # Mock a Sphinx app
    class MockApp:
        def __init__(self):
            self.config_values = {}
            self.connections = {}

        def add_config_value(self, name, default, rebuild):
            self.config_values[name] = (default, rebuild)

        def connect(self, event, handler):
            self.connections[event] = handler

    app = MockApp()
    result = setup(app)

    # Check that result is a dict
    assert isinstance(result, dict)
    assert "version" in result
    assert "parallel_read_safe" in result
    assert "parallel_write_safe" in result


def test_builder_inited_with_disallowed_builder():
    """Test that disallowed builders do not trigger extension setup."""
    import sphinx_llms_txt

    # Reset global state
    sphinx_llms_txt._manager = sphinx_llms_txt.LLMSFullManager()
    sphinx_llms_txt._root_first_paragraph = ""

    # Mock a Sphinx app with a disallowed builder
    class MockBuilder:
        name = "text"  # Not in allowed list

    class MockApp:
        def __init__(self):
            self.config_values = {}
            self.connections = {}
            self.builder = MockBuilder()

        def add_config_value(self, name, default, rebuild):
            self.config_values[name] = (default, rebuild)

        def connect(self, event, handler):
            self.connections[event] = handler

    app = MockApp()
    setup(app)

    # Trigger builder-inited
    builder_inited_handler = app.connections["builder-inited"]
    builder_inited_handler(app)

    # With disallowed builder, other events should NOT be connected
    assert "doctree-resolved" not in app.connections
    assert "build-finished" not in app.connections


def test_document_collector_initialization():
    """Test initialization of DocumentCollector."""
    collector = DocumentCollector()
    assert collector.page_titles == {}
    assert collector.config == {}
    assert collector.master_doc is None
    assert collector.env is None


def test_document_processor_initialization():
    """Test initialization of DocumentProcessor."""
    config = {"llms_txt_directives": []}
    processor = DocumentProcessor(config)
    assert processor.config == config
    assert processor.srcdir is None


def test_file_writer_initialization():
    """Test initialization of FileWriter."""
    config = {"llms_txt_filename": "llms.txt"}
    writer = FileWriter(config)
    assert writer.config == config
    assert writer.outdir is None
    assert writer.app is None


def test_llms_full_manager_initialization():
    """Test initialization of LLMSFullManager."""
    manager = LLMSFullManager()
    assert manager.config == {}
    assert isinstance(manager.collector, DocumentCollector)
    assert manager.processor is None
    assert manager.writer is None
    assert manager.master_doc is None
    assert manager.env is None


def test_collector_page_title_update():
    """Test updating page titles."""
    collector = DocumentCollector()
    collector.update_page_title("doc1", "Title 1")
    collector.update_page_title("doc2", "Title 2")

    assert collector.page_titles["doc1"] == "Title 1"
    assert collector.page_titles["doc2"] == "Title 2"


def test_manager_page_title_update():
    """Test updating page titles through manager."""
    manager = LLMSFullManager()
    manager.update_page_title("doc1", "Title 1")
    manager.update_page_title("doc2", "Title 2")

    assert manager.collector.page_titles["doc1"] == "Title 1"
    assert manager.collector.page_titles["doc2"] == "Title 2"


def test_set_config():
    """Test setting configuration."""
    manager = LLMSFullManager()
    config = {
        "llms_txt_full_filename": "custom.txt",
        "llms_txt_file": True,
        "llms_txt_full_max_size": 1000,
    }
    manager.set_config(config)
    assert manager.config == config
    assert manager.collector.config == config
    assert isinstance(manager.processor, DocumentProcessor)
    assert isinstance(manager.writer, FileWriter)


def test_set_master_doc():
    """Test setting master doc."""
    manager = LLMSFullManager()
    manager.set_master_doc("index")
    assert manager.master_doc == "index"
    assert manager.collector.master_doc == "index"


def test_empty_page_order():
    """Test get_page_order returns empty list when env or master_doc not set."""
    collector = DocumentCollector()
    assert collector.get_page_order() == []

    # Set only master_doc, but not env
    collector.set_master_doc("index")
    assert collector.get_page_order() == []


def test_process_includes(tmp_path):
    """Test that include directives are processed correctly."""
    # Create a processor
    config = {"llms_txt_directives": []}
    processor = DocumentProcessor(config)

    # Create a test file with an include directive
    include_content = "This is included content.\nWith multiple lines."
    include_file = tmp_path / "included.txt"
    with open(include_file, "w", encoding="utf-8") as f:
        f.write(include_content)

    # Create a source file that includes the test file
    source_content = (
        "Line before include.\n.. include:: included.txt\nLine after include."
    )
    source_file = tmp_path / "source.txt"
    with open(source_file, "w", encoding="utf-8") as f:
        f.write(source_content)

    # Process the include directive
    processed_content = processor._process_includes(source_content, source_file)

    # Check that the include directive was replaced with the content
    expected_content = (
        "Line before include.\nThis is included content.\nWith multiple"
        " lines.\nLine after include."
    )
    assert processed_content == expected_content


def test_process_includes_with_relative_paths(tmp_path):
    """Test that include directives with relative paths are processed correctly."""
    # Create a processor
    config = {"llms_txt_directives": []}

    # Set up a more complex directory structure
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()

    # Create the original source directory structure
    source_dir = docs_dir / "source"
    source_dir.mkdir()

    # Create a subdirectory
    subdir = source_dir / "subdir"
    subdir.mkdir()

    # Create an includes directory
    includes_dir = source_dir / "includes"
    includes_dir.mkdir()

    # Create a processor with srcdir
    processor = DocumentProcessor(config, str(source_dir))

    # Create the included file in the includes directory
    include_content = "This is included content from another directory."
    include_file = includes_dir / "common.txt"
    with open(include_file, "w", encoding="utf-8") as f:
        f.write(include_content)

    # Create a source file in the subdirectory that includes the file from includes
    source_content = (
        "Line before include.\n.. include:: ../includes/common.txt\nLine after include."
    )
    source_file = subdir / "page.txt"
    with open(source_file, "w", encoding="utf-8") as f:
        f.write(source_content)

    # Create the _sources directory to mimic Sphinx build output
    build_dir = tmp_path / "build"
    build_dir.mkdir()
    sources_dir = build_dir / "_sources"
    sources_dir.mkdir()

    # Create the same structure in the _sources directory
    sources_subdir = sources_dir / "subdir"
    sources_subdir.mkdir()

    # Copy the source file to the _sources directory
    sources_file = sources_subdir / "page.txt"
    with open(sources_file, "w", encoding="utf-8") as f:
        f.write(source_content)

    # Process the include directive from the _sources file
    processed_content = processor._process_includes(source_content, sources_file)

    # Check that the include directive was replaced with the content
    expected_content = (
        "Line before include.\nThis is included content from another"
        " directory.\nLine after include."
    )
    assert processed_content == expected_content


def test_match_exclude_pattern():
    """Test the _match_exclude_pattern method."""
    # Create a collector
    collector = DocumentCollector()

    # Test exact match
    assert collector._match_exclude_pattern("page1", "page1") is True
    assert collector._match_exclude_pattern("page1", "page2") is False

    # Test glob-style patterns
    assert collector._match_exclude_pattern("page1", "page*") is True
    assert collector._match_exclude_pattern("page_with_include", "page_with_*") is True
    assert collector._match_exclude_pattern("page1", "*1") is True
    assert collector._match_exclude_pattern("subdir/page1", "*/page1") is True
    assert collector._match_exclude_pattern("page1", "subdir/*") is False


def test_write_verbose_info_to_file(tmp_path):
    """Test writing verbose info to a file."""
    # Create a build directory
    build_dir = tmp_path / "build"
    build_dir.mkdir()

    # Create writer with configuration and outdir
    config = {
        "llms_txt_file": True,
        "llms_txt_full_max_size": 1000,
        "llms_txt_filename": "llms.txt",
    }
    writer = FileWriter(config, str(build_dir))

    # Create page titles
    page_titles = {
        "index": "Home Page",
        "about": "About Us",
    }

    # Create a page order
    page_order = ["index", "about"]

    # Call the method to write verbose info to file
    writer.write_verbose_info_to_file(page_order, page_titles)

    # Check that the file was created
    verbose_file = build_dir / "llms.txt"
    assert verbose_file.exists()

    # Read the file content
    with open(verbose_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Check that the content contains expected information
    assert "## Docs" in content
    # Without html_baseurl, URLs should start with /
    assert "- [Home Page](/index.html)" in content
    assert "- [About Us](/about.html)" in content


def test_write_verbose_info_with_baseurl(tmp_path):
    """Test writing verbose info to a file with html_baseurl set."""
    # Create a build directory
    build_dir = tmp_path / "build"
    build_dir.mkdir()

    # Create writer with configuration including html_baseurl
    config = {
        "llms_txt_file": True,
        "llms_txt_full_max_size": 1000,
        "llms_txt_filename": "llms.txt",
        "html_baseurl": "https://example.com",
    }
    writer = FileWriter(config, str(build_dir))

    # Create page titles
    page_titles = {
        "index": "Home Page",
        "about": "About Us",
    }

    # Create a page order
    page_order = ["index", "about"]

    # Call the method to write verbose info to file
    writer.write_verbose_info_to_file(page_order, page_titles)

    # Check that the file was created
    verbose_file = build_dir / "llms.txt"
    assert verbose_file.exists()

    # Read the file content
    with open(verbose_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Check that the content contains expected information with baseurl
    assert "## Docs" in content
    assert "- [Home Page](https://example.com/index.html)" in content
    assert "- [About Us](https://example.com/about.html)" in content

    # Test with baseurl without trailing slash
    config["html_baseurl"] = "https://example.org"
    writer = FileWriter(config, str(build_dir))
    writer.write_verbose_info_to_file(page_order, page_titles)

    with open(verbose_file, "r", encoding="utf-8") as f:
        content = f.read()

    assert "- [Home Page](https://example.org/index.html)" in content
    assert "- [About Us](https://example.org/about.html)" in content


def test_get_source_suffixes_with_dict():
    """Test _get_source_suffixes method with dict source_suffix."""
    from sphinx_llms_txt.manager import LLMSFullManager

    # Mock Sphinx app with dict source_suffix
    class MockApp:
        class Config:
            source_suffix = {".rst": None, ".md": None, ".txt": None}

        config = Config()

    manager = LLMSFullManager()
    manager.set_app(MockApp())

    suffixes = manager._get_source_suffixes()
    assert set(suffixes) == {".rst", ".md", ".txt"}


def test_get_source_suffixes_with_list():
    """Test _get_source_suffixes method with list source_suffix."""
    from sphinx_llms_txt.manager import LLMSFullManager

    # Mock Sphinx app with list source_suffix
    class MockApp:
        class Config:
            source_suffix = [".rst", ".md"]

        config = Config()

    manager = LLMSFullManager()
    manager.set_app(MockApp())

    suffixes = manager._get_source_suffixes()
    assert suffixes == [".rst", ".md"]


def test_get_source_suffixes_with_string():
    """Test _get_source_suffixes method with string source_suffix."""
    from sphinx_llms_txt.manager import LLMSFullManager

    # Mock Sphinx app with string source_suffix
    class MockApp:
        class Config:
            source_suffix = ".rst"

        config = Config()

    manager = LLMSFullManager()
    manager.set_app(MockApp())

    suffixes = manager._get_source_suffixes()
    assert suffixes == [".rst"]


def test_get_source_suffixes_no_app():
    """Test _get_source_suffixes method with no app set."""
    from sphinx_llms_txt.manager import LLMSFullManager

    manager = LLMSFullManager()

    suffixes = manager._get_source_suffixes()
    assert suffixes == [".rst"]  # Default fallback


def test_html_sourcelink_suffix_default():
    """Test html_sourcelink_suffix defaults to .txt when no app is set."""
    import tempfile

    from sphinx_llms_txt.manager import LLMSFullManager

    manager = LLMSFullManager()
    manager.set_config(
        {
            "llms_txt_full_filename": "test.txt",
            "llms_txt_exclude": [],
            "llms_txt_directives": [],
        }
    )

    # Create a temporary directory structure
    with tempfile.TemporaryDirectory() as tmpdir:
        outdir = f"{tmpdir}/build"
        srcdir = f"{tmpdir}/source"
        sources_dir = f"{outdir}/_sources"

        # Create directories
        import os

        os.makedirs(sources_dir, exist_ok=True)
        os.makedirs(srcdir, exist_ok=True)

        # Create a test source file with default .txt suffix
        test_file = f"{sources_dir}/index.rst.txt"
        with open(test_file, "w") as f:
            f.write("Test content")

        # Mock env with minimal required attributes
        class MockEnv:
            all_docs = {"index": None}
            titles = {
                "index": type("TitleNode", (), {"astext": lambda: "Test Title"})()
            }
            toctree_includes = {}

        manager.set_env(MockEnv())
        manager.set_master_doc("index")

        # Test that it uses .txt as the default suffix
        manager.combine_sources(outdir, srcdir)

        # Verify the file was found and processed (check if output file exists)
        output_file = f"{outdir}/test.txt"
        assert os.path.exists(output_file)


def test_html_sourcelink_suffix_custom():
    """Test html_sourcelink_suffix uses custom value from Sphinx config."""
    import tempfile

    from sphinx_llms_txt.manager import LLMSFullManager

    # Mock Sphinx app with custom html_sourcelink_suffix
    class MockApp:
        class Config:
            html_sourcelink_suffix = "source"
            source_suffix = ".rst"

        config = Config()

    manager = LLMSFullManager()
    manager.set_app(MockApp())
    manager.set_config(
        {
            "llms_txt_full_filename": "test.txt",
            "llms_txt_exclude": [],
            "llms_txt_directives": [],
        }
    )

    # Create a temporary directory structure
    with tempfile.TemporaryDirectory() as tmpdir:
        outdir = f"{tmpdir}/build"
        srcdir = f"{tmpdir}/source"
        sources_dir = f"{outdir}/_sources"

        # Create directories
        import os

        os.makedirs(sources_dir, exist_ok=True)
        os.makedirs(srcdir, exist_ok=True)

        # Create a test source file with custom .source suffix
        test_file = f"{sources_dir}/index.rst.source"
        with open(test_file, "w") as f:
            f.write("Test content")

        # Mock env with minimal required attributes
        class MockEnv:
            all_docs = {"index": None}
            titles = {
                "index": type("TitleNode", (), {"astext": lambda: "Test Title"})()
            }
            toctree_includes = {}

        manager.set_env(MockEnv())
        manager.set_master_doc("index")

        # Test that it uses .source as the custom suffix
        manager.combine_sources(outdir, srcdir)

        # Verify the file was found and processed
        output_file = f"{outdir}/test.txt"
        assert os.path.exists(output_file)


def test_html_sourcelink_suffix_with_dot():
    """Test html_sourcelink_suffix adds dot if missing."""
    import tempfile

    from sphinx_llms_txt.manager import LLMSFullManager

    # Mock Sphinx app with html_sourcelink_suffix without leading dot
    class MockApp:
        class Config:
            html_sourcelink_suffix = "src"  # No leading dot
            source_suffix = ".rst"

        config = Config()

    manager = LLMSFullManager()
    manager.set_app(MockApp())
    manager.set_config(
        {
            "llms_txt_full_filename": "test.txt",
            "llms_txt_exclude": [],
            "llms_txt_directives": [],
        }
    )

    # Create a temporary directory structure
    with tempfile.TemporaryDirectory() as tmpdir:
        outdir = f"{tmpdir}/build"
        srcdir = f"{tmpdir}/source"
        sources_dir = f"{outdir}/_sources"

        # Create directories
        import os

        os.makedirs(sources_dir, exist_ok=True)
        os.makedirs(srcdir, exist_ok=True)

        # Create a test source file with .src suffix (dot should be added automatically)
        test_file = f"{sources_dir}/index.rst.src"
        with open(test_file, "w") as f:
            f.write("Test content")

        # Mock env with minimal required attributes
        class MockEnv:
            all_docs = {"index": None}
            titles = {
                "index": type("TitleNode", (), {"astext": lambda: "Test Title"})()
            }
            toctree_includes = {}

        manager.set_env(MockEnv())
        manager.set_master_doc("index")

        # Test that it adds the dot and finds the file
        manager.combine_sources(outdir, srcdir)

        # Verify the file was found and processed
        output_file = f"{outdir}/test.txt"
        assert os.path.exists(output_file)


def test_mixed_source_file_formats():
    """Test handling of mixed source file formats (.rst, .md, .txt)."""
    import tempfile

    from sphinx_llms_txt.manager import LLMSFullManager

    # Mock Sphinx app with multiple source suffixes
    class MockApp:
        class Config:
            html_sourcelink_suffix = ".txt"
            source_suffix = {".rst": None, ".md": None, ".txt": None}

        config = Config()

    manager = LLMSFullManager()
    manager.set_app(MockApp())
    manager.set_config(
        {
            "llms_txt_full_filename": "test.txt",
            "llms_txt_exclude": [],
            "llms_txt_directives": [],
        }
    )

    # Create a temporary directory structure
    with tempfile.TemporaryDirectory() as tmpdir:
        outdir = f"{tmpdir}/build"
        srcdir = f"{tmpdir}/source"
        sources_dir = f"{outdir}/_sources"

        # Create directories
        import os

        os.makedirs(sources_dir, exist_ok=True)
        os.makedirs(srcdir, exist_ok=True)

        # Create test source files with different formats
        files_to_create = [
            f"{sources_dir}/page1.rst.txt",
            f"{sources_dir}/page2.md.txt",
            f"{sources_dir}/page3.txt.txt",
        ]

        for test_file in files_to_create:
            with open(test_file, "w") as f:
                f.write(f"Content for {os.path.basename(test_file)}")

        # Mock env with all documents
        class MockEnv:
            all_docs = {"page1": None, "page2": None, "page3": None}
            titles = {
                "page1": type("TitleNode", (), {"astext": lambda: "Page 1"})(),
                "page2": type("TitleNode", (), {"astext": lambda: "Page 2"})(),
                "page3": type("TitleNode", (), {"astext": lambda: "Page 3"})(),
            }
            toctree_includes = {}

        manager.set_env(MockEnv())
        manager.set_master_doc("page1")

        # Test that all file formats are found and processed
        manager.combine_sources(outdir, srcdir)

        # Verify the output file was created and contains content from all formats
        output_file = f"{outdir}/test.txt"
        assert os.path.exists(output_file)

        with open(output_file, "r") as f:
            content = f.read()

        # Should contain content from all three files
        assert "Content for page1.rst.txt" in content
        assert "Content for page2.md.txt" in content
        assert "Content for page3.txt.txt" in content


def test_source_suffix_detection_priority():
    """Test source suffix detection tries formats in correct order for docnames."""
    import tempfile

    from sphinx_llms_txt.manager import LLMSFullManager

    # Mock Sphinx app with ordered source suffixes
    class MockApp:
        class Config:
            html_sourcelink_suffix = ".txt"
            source_suffix = [".rst", ".md"]  # rst has priority over md

        config = Config()

    manager = LLMSFullManager()
    manager.set_app(MockApp())
    manager.set_config(
        {
            "llms_txt_full_filename": "test.txt",
            "llms_txt_exclude": [],
            "llms_txt_directives": [],
        }
    )

    # Create a temporary directory structure
    with tempfile.TemporaryDirectory() as tmpdir:
        outdir = f"{tmpdir}/build"
        srcdir = f"{tmpdir}/source"
        sources_dir = f"{outdir}/_sources"

        # Create directories
        import os

        os.makedirs(sources_dir, exist_ok=True)
        os.makedirs(srcdir, exist_ok=True)

        # Create both .rst and .md versions of the same document
        # Only create files for the specific docname "index"
        rst_file = f"{sources_dir}/index.rst.txt"
        md_file = f"{sources_dir}/index.md.txt"

        with open(rst_file, "w") as f:
            f.write("RST content for index")

        with open(md_file, "w") as f:
            f.write("Markdown content for index")

        # Mock env with only the index document
        class MockEnv:
            all_docs = {"index": None}
            titles = {
                "index": type("TitleNode", (), {"astext": lambda: "Index Page"})()
            }
            toctree_includes = {"index": []}

        manager.set_env(MockEnv())
        manager.set_master_doc("index")

        # Test the priority behavior
        manager.combine_sources(outdir, srcdir)

        # Check that output file was created
        output_file = f"{outdir}/test.txt"
        assert os.path.exists(output_file)

        with open(output_file, "r") as f:
            content = f.read()

        # The system should prefer RST over MD for the "index" docname
        # But since both files exist and the second phase adds remaining files,
        # both will be included. The test verifies that RST appears first
        # (indicating it was found first in the priority order)
        assert "RST content for index" in content

        # Find positions to verify order
        rst_pos = content.find("RST content for index")
        md_pos = content.find("Markdown content for index")

        # RST should come before MD (due to priority in toctree processing)
        assert rst_pos < md_pos, "RST content should appear before MD content"


def test_summary_default_uses_first_paragraph():
    """
    Test that summary defaults to first paragraph of root document when not configured.
    """
    from docutils import nodes
    from docutils.frontend import OptionParser
    from docutils.parsers.rst import Parser
    from docutils.utils import new_document

    from sphinx_llms_txt import build_finished, doctree_resolved

    # Create a proper document with settings
    settings = OptionParser(components=(Parser,)).get_default_values()
    doctree = new_document("<rst-doc>", settings)

    title = nodes.title(text="Test Title")
    paragraph = nodes.paragraph(
        text="This is the first paragraph that should be used as summary."
    )
    doctree.append(title)
    doctree.append(paragraph)

    # Mock Sphinx app
    class MockApp:
        class Config:
            master_doc = "index"
            llms_txt_summary = None  # Not configured
            llms_txt_file = True
            llms_txt_filename = "llms.txt"
            llms_txt_title = None
            llms_txt_full_file = True
            llms_txt_full_filename = "llms-full.txt"
            llms_txt_full_max_size = None
            llms_txt_full_size_policy = "warn_skip"
            llms_txt_directives = []
            llms_txt_exclude = []
            llms_txt_code_files = []
            llms_txt_code_base_path = None
            html_baseurl = ""

        config = Config()
        outdir = "/tmp/build"
        srcdir = "/tmp/source"

        class Env:
            titles = {
                "index": type("TitleNode", (), {"astext": lambda self: "Test Title"})()
            }

        env = Env()

    app = MockApp()

    # Reset the global state
    import sphinx_llms_txt

    sphinx_llms_txt._root_first_paragraph = ""

    # Call doctree_resolved to extract the first paragraph
    doctree_resolved(app, doctree, "index")

    # Verify the first paragraph was extracted
    assert (
        sphinx_llms_txt._root_first_paragraph
        == "This is the first paragraph that should be used as summary."
    )

    # Mock the manager methods to avoid actual file operations
    original_combine_sources = sphinx_llms_txt._manager.combine_sources
    sphinx_llms_txt._manager.combine_sources = lambda outdir, srcdir: None

    # Call build_finished and verify the summary is set correctly
    build_finished(app, None)

    # Check that the summary was properly configured
    assert (
        sphinx_llms_txt._manager.config["llms_txt_summary"]
        == "This is the first paragraph that should be used as summary."
    )

    # Restore original method
    sphinx_llms_txt._manager.combine_sources = original_combine_sources


def test_code_files_include_exclude_patterns(tmp_path):
    """Test the +/- pattern syntax for llms_txt_code_files configuration."""
    from sphinx_llms_txt.manager import LLMSFullManager

    # Create test directory structure
    src_dir = tmp_path / "src"
    src_dir.mkdir()

    docs_dir = src_dir / "docs"
    docs_dir.mkdir()

    cache_dir = docs_dir / "__pycache__"
    cache_dir.mkdir()

    # Create test files
    (docs_dir / "example.rst").write_text("Example RST content")
    (docs_dir / "guide.rst").write_text("Guide RST content")
    (docs_dir / "backup.bak").write_text("Backup file content")
    (cache_dir / "compiled.pyc").write_text("Compiled Python")

    # Create manager and set source directory
    manager = LLMSFullManager()
    manager.srcdir = str(src_dir)

    # Test configuration with include/exclude patterns
    config = {
        "llms_txt_code_files": [
            "+:docs/**/*.rst",  # Include all RST files in docs
            "-:docs/**/__pycache__/**",  # Exclude pycache files
            "-:docs/**/*.bak",  # Exclude backup files
        ]
    }
    manager.set_config(config)

    # Process code files
    code_parts, _ = manager._process_code_files()

    # Verify we have the expected number of files
    assert len(code_parts) == 2, f"Expected 2 files, got {len(code_parts)}"

    # Extract file titles from code blocks
    titles = []
    for part in code_parts:
        lines = part.strip().split("\n")
        if lines:
            titles.append(lines[0])

    # Verify expected files are included
    assert "docs/example.rst" in titles
    assert "docs/guide.rst" in titles

    # Verify excluded files are not present
    content = "\n".join(code_parts)
    assert "backup.bak" not in content
    assert "__pycache__" not in content
    assert "compiled.pyc" not in content


def test_code_files_exclude_only_patterns(tmp_path):
    """Test that exclude-only patterns result in no files being included."""
    from sphinx_llms_txt.manager import LLMSFullManager

    # Create test directory structure
    src_dir = tmp_path / "src"
    src_dir.mkdir()

    docs_dir = src_dir / "docs"
    docs_dir.mkdir()

    # Create test files
    (docs_dir / "example.rst").write_text("Example RST content")

    # Create manager and set source directory
    manager = LLMSFullManager()
    manager.srcdir = str(src_dir)

    # Test configuration with only exclude patterns
    config = {
        "llms_txt_code_files": [
            "-:docs/**/*.rst",  # Only exclude pattern, no includes
        ]
    }
    manager.set_config(config)

    # Process code files
    code_parts, _ = manager._process_code_files()

    # Should have no files with exclude-only patterns
    assert len(code_parts) == 0, "Should have no files with exclude-only patterns"


def test_code_files_no_prefix_patterns(tmp_path):
    """Test that patterns without prefix are ignored."""
    from sphinx_llms_txt.manager import LLMSFullManager

    # Create test directory structure
    src_dir = tmp_path / "src"
    src_dir.mkdir()

    docs_dir = src_dir / "docs"
    docs_dir.mkdir()

    # Create test files
    (docs_dir / "example.rst").write_text("Example RST content")
    (docs_dir / "backup.bak").write_text("Backup file content")

    # Create manager and set source directory
    manager = LLMSFullManager()
    manager.srcdir = str(src_dir)

    # Test configuration with no prefix (should be ignored)
    config = {
        "llms_txt_code_files": [
            "docs/**/*.rst",  # No prefix = ignored
            "+:docs/**/*.rst",  # Include RST files
            "-:docs/**/*.bak",  # Exclude backup files
        ]
    }
    manager.set_config(config)

    # Process code files
    code_parts, _ = manager._process_code_files()

    # Should include RST files (from +: pattern) and exclude BAK files (from -: pattern)
    assert len(code_parts) == 1, "Should include RST files and exclude BAK files"

    content = "\n".join(code_parts)
    assert "Example RST content" in content
    assert "backup.bak" not in content


def test_code_files_ignored_patterns(tmp_path, caplog):
    """Test that patterns without +: or -: prefix log a warning and are ignored."""
    from unittest.mock import patch

    from sphinx_llms_txt.manager import LLMSFullManager

    # Create test directory structure
    src_dir = tmp_path / "src"
    src_dir.mkdir()

    docs_dir = src_dir / "docs"
    docs_dir.mkdir()

    # Create test files
    (docs_dir / "example.rst").write_text("Example RST content")

    # Use a mock to capture the warning message directly
    captured_warnings = []

    def capture_warning(message, *args, **kwargs):
        captured_warnings.append(message)

    # Patch the logger to capture warnings
    with patch("sphinx_llms_txt.manager.logger.warning", side_effect=capture_warning):
        # Create manager and set source directory
        manager = LLMSFullManager()
        manager.srcdir = str(src_dir)

        # Test configuration with only no-prefix patterns (should result in no files)
        config = {
            "llms_txt_code_files": [
                "docs/**/*.rst",  # No prefix = ignored with warning
            ]
        }
        manager.set_config(config)

        # Process code files
        code_parts, _ = manager._process_code_files()

    # Should have no files since the pattern without prefix is ignored
    assert (
        len(code_parts) == 0
    ), "Should have no files when only using patterns without prefix"

    # Check that a warning was logged
    assert (
        len(captured_warnings) == 1
    ), f"Expected 1 warning, got {len(captured_warnings)}"
    assert (
        "Code file pattern 'docs/**/*.rst' ignored." in captured_warnings[0]
    ), f"Warning message should contain expected text. Got: {captured_warnings[0]}"


def test_llms_txt_generated_without_sources_dir(tmp_path):
    """Test that llms.txt is generated even when _sources directory doesn't exist."""

    from sphinx_llms_txt.manager import LLMSFullManager

    # Create manager
    manager = LLMSFullManager()

    # Set config to enable llms.txt
    config = {
        "llms_txt_file": True,
        "llms_txt_filename": "llms.txt",
        "llms_txt_full_file": True,
        "llms_txt_full_filename": "llms-full.txt",
        "llms_txt_exclude": [],
        "llms_txt_directives": [],
    }
    manager.set_config(config)

    # Create directories (but no _sources)
    outdir = tmp_path / "build"
    srcdir = tmp_path / "source"
    outdir.mkdir()
    srcdir.mkdir()

    # Mock env with documents
    class MockEnv:
        all_docs = {"index": None, "about": None}
        titles = {
            "index": type("TitleNode", (), {"astext": lambda self: "Home"})(),
            "about": type("TitleNode", (), {"astext": lambda self: "About"})(),
        }
        toctree_includes = {"index": ["about"]}

    manager.set_env(MockEnv())
    manager.set_master_doc("index")

    # Update page titles directly in the collector
    manager.update_page_title("index", "Home")
    manager.update_page_title("about", "About")

    # Call combine_sources - should generate llms.txt even without _sources
    manager.combine_sources(str(outdir), str(srcdir))

    # Verify llms.txt was created
    llms_txt = outdir / "llms.txt"
    assert llms_txt.exists(), "llms.txt should be generated even without _sources"

    # Verify llms-full.txt was NOT created (since no _sources)
    llms_full_txt = outdir / "llms-full.txt"
    assert (
        not llms_full_txt.exists()
    ), "llms-full.txt should not be generated without _sources"

    # Read llms.txt and verify it has content
    with open(llms_txt, "r", encoding="utf-8") as f:
        content = f.read()

    # Should contain page titles and links
    assert "Home" in content
    assert "About" in content
    assert "index.html" in content
    assert "about.html" in content


def test_llms_txt_no_warning_when_full_file_disabled(tmp_path, caplog):
    """
    Test that no warning is logged when llms_txt_full_file=False and
    _sources doesn't exist.
    """
    from unittest.mock import patch

    from sphinx_llms_txt.manager import LLMSFullManager

    # Create manager
    manager = LLMSFullManager()

    # Set config with llms_txt_full_file=False
    config = {
        "llms_txt_file": True,
        "llms_txt_filename": "llms.txt",
        "llms_txt_full_file": False,  # User doesn't want llms-full.txt
        "llms_txt_full_filename": "llms-full.txt",
        "llms_txt_exclude": [],
        "llms_txt_directives": [],
    }
    manager.set_config(config)

    # Create directories (but no _sources)
    outdir = tmp_path / "build"
    srcdir = tmp_path / "source"
    outdir.mkdir()
    srcdir.mkdir()

    # Mock env with documents
    class MockEnv:
        all_docs = {"index": None}
        titles = {"index": type("TitleNode", (), {"astext": lambda self: "Home"})()}
        toctree_includes = {"index": []}

    manager.set_env(MockEnv())
    manager.set_master_doc("index")
    manager.update_page_title("index", "Home")

    # Capture warnings
    captured_warnings = []

    def capture_warning(message, *args, **kwargs):
        if "_sources" in str(message):
            captured_warnings.append(message)

    with patch("sphinx_llms_txt.manager.logger.warning", side_effect=capture_warning):
        # Call combine_sources
        manager.combine_sources(str(outdir), str(srcdir))

    # Verify NO warning was logged since llms_txt_full_file=False
    assert (
        len(captured_warnings) == 0
    ), "No warning should be logged when llms_txt_full_file=False"

    # Verify llms.txt was still created
    llms_txt = outdir / "llms.txt"
    assert llms_txt.exists()
