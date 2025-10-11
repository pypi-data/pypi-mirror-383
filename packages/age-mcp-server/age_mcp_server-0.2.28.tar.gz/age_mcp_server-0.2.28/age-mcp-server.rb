class AgeMcpServer < Formula
  include Language::Python::Virtualenv

  desc "Apache AGE MCP Server"
  homepage "https://github.com/rioriost/homebrew-age-mcp-server/"
  url "https://files.pythonhosted.org/packages/94/40/1c6ea9b08dcbac0dfd9e369665e0529ac4cc802df5ccdb5468ded4a668c3/age_mcp_server-0.2.27.tar.gz"
  sha256 "86c5dd0c1433222801463a019836ab10a7429b033a996947ec6f9ede15acbdd7"
  license "MIT"

  depends_on "python@3.13"

  resource "agefreighter" do
    url "https://files.pythonhosted.org/packages/f4/1a/9703a6c6d5e915f2829ac1d75527654858ce3bbd35b3f1800333a0f3d1ca/agefreighter-1.0.17.tar.gz"
    sha256 "8df2262cfc8cb1a1772b8204f5fcc9afe7fc02f1d7c1c71a604acd29d67014c0"
  end

  resource "ply" do
    url "https://files.pythonhosted.org/packages/e5/69/882ee5c9d017149285cab114ebeab373308ef0f874fcdac9beb90e0ac4da/ply-3.11.tar.gz"
    sha256 "00c7c1aaa88358b9c765b6d3000c6eec0ba42abca5351b095321aef446081da3"
  end

  def install
    virtualenv_install_with_resources
    system libexec/"bin/python", "-m", "pip", "install", "psycopg[binary,pool]", "mcp"
  end

  test do
    system "#{bin}/age-mcp-server", "--help"
  end
end
