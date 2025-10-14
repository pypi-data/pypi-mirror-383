const Avatar = ({ initial, bordered = false }) => {
  const className = Whitebox.utils.getClasses(
      "w-10 h-10 bg-gray-5 rounded-full flex items-center justify-center",
      "text-gray-1 font-medium",
      bordered ? "border-2 border-gray-4" : "",
  )
  return (
    <div className={className}>
      {initial}
    </div>
  );
};

export default Avatar;
