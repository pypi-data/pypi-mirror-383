class Trmd < Formula
  include Language::Python::Virtualenv

  desc "Translate Markdown using OpenAI"
  homepage "https://github.com/rioriost/homebrew-trmd/"
  url "https://files.pythonhosted.org/packages/eb/f2/545dde8e8b9bd8aee62c2953acf6d5b2812af1a7ba85e20f65d3bb97f333/trmd-0.1.21.tar.gz"
  sha256 "20afd8e98ad180dc24cd9ae571e39b4d0ac2cd409cb33dab88baac847a60e762"
  license "MIT"

  depends_on "python@3.13"

  def install
    virtualenv_install_with_resources
    system libexec/"bin/python", "-m", "pip", "install", "openai"
  end

  test do
    system "#{bin}/trmd", "--help"
  end
end
