class VibeCli < Formula
  include Language::Python::Virtualenv

  desc "Natural language interface for developer tools"
  homepage "https://github.com/yourusername/vibe-cli"
  url "https://github.com/yourusername/vibe-cli/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "0000000000000000000000000000000000000000000000000000000000000000" # Placeholder for real SHA
  license "MIT"
  head "https://github.com/yourusername/vibe-cli.git", branch: "main"

  depends_on "python@3.9"

  resource "typer" do
    url "https://files.pythonhosted.org/packages/cf/d9/f3d39a6d78134cb1f13ddf90061818534569d07f29f56ad08aa6b3c03fe5/typer-0.9.0.tar.gz"
    sha256 "50922fd79aea2f4751a8e0408ff10d2662bd0c8bbfa84755a699f3bada79963b"
  end

  def install
    virtualenv_install_with_resources
    bin.install_symlink "#{libexec}/bin/vibe"
  end

  test do
    assert_match "Vibe CLI", shell_output("#{bin}/vibe version")
  end
end
