export default function StatusBadge({ status, label }) {
    const statusColors = {
        success: 'bg-green-500',
        warning: 'bg-yellow-500',
        error: 'bg-red-500',
        info: 'bg-blue-500',
        neutral: 'bg-gray-500',
    };

    return (
        <div className="flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${statusColors[status] || statusColors.neutral} animate-pulse`}></span>
            <span className="text-sm text-gray-300">{label}</span>
        </div>
    );
}
